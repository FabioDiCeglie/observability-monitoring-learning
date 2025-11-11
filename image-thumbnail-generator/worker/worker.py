import json
import time
from datetime import datetime
from shared.database import init_db, get_db, Image, Thumbnail, ImageStatus
from shared.pubsub_client import get_pubsub_client
from shared.config import Config
from shared.metrics import init_metrics, increment_counter, record_histogram, record_timing
from worker.processors.image_processor import generate_thumbnails

init_metrics()


def process_image_message(message_data: dict, db):
    """Process a single image message."""
    image_id = message_data.get("image_id")
    file_path = message_data.get("file_path")
    
    print(f"🔄 Processing image: {image_id}")
    start_time = time.time()
    
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        print(f"❌ Image not found in database: {image_id}")
        increment_counter("worker.process.count", tags=["status:error", "reason:not_found"])
        return False
    
    image.status = ImageStatus.PROCESSING
    db.commit()
    
    try:
        thumbnails = generate_thumbnails(file_path, image_id)
        
        for size_name, width, height, thumb_path, file_size, proc_time_ms in thumbnails:
            thumbnail = Thumbnail(
                image_id=image_id,
                size_name=size_name,
                width=width,
                height=height,
                file_path=thumb_path,
                file_size_bytes=file_size,
                processing_time_ms=proc_time_ms
            )
            db.add(thumbnail)
            
            record_timing(f"thumbnail.generation.time", proc_time_ms, tags=[f"size:{size_name}"])
            record_histogram(f"thumbnail.size_bytes", file_size, tags=[f"size:{size_name}"])
        
        image.status = ImageStatus.COMPLETED
        image.processed_at = datetime.utcnow()
        db.commit()
        
        total_time_ms = (time.time() - start_time) * 1000
        record_timing("worker.process.total_time", total_time_ms)
        increment_counter("worker.process.count", tags=["status:success"])
        
        print(f"✅ Completed processing: {image_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {image_id}: {e}")
        image.status = ImageStatus.FAILED
        image.error_message = str(e)
        db.commit()
        increment_counter("worker.process.count", tags=["status:error", "reason:processing_failed"])
        return False


def main():
    print("🚀 Starting Image Worker...")
    
    init_db()
    pubsub_client = get_pubsub_client()
    
    print(f"👂 Listening for messages...")
    print(f"   Sleep interval: {Config.WORKER_SLEEP_SECONDS}s")
    
    while True:
        try:
            messages = pubsub_client.pull_messages(max_messages=1, timeout=5.0)
            
            if not messages:
                time.sleep(Config.WORKER_SLEEP_SECONDS)
                continue
            
            for received_message in messages:
                try:
                    message_data = json.loads(received_message.message.data.decode("utf-8"))
                    print(f"📥 Received message: {message_data.get('image_id')}")
                    
                    db_gen = get_db()
                    db = next(db_gen)
                    try:
                        success = process_image_message(message_data, db)
                    finally:
                        try:
                            next(db_gen)
                        except StopIteration:
                            pass
                    
                    if success:
                        pubsub_client.acknowledge_message(received_message.ack_id)
                    else:
                        pubsub_client.nack_message(received_message.ack_id)
                        
                except Exception as e:
                    import traceback
                    print(f"❌ Error handling message: {e}")
                    print(f"   Traceback: {traceback.format_exc()}")
                    pubsub_client.nack_message(received_message.ack_id)
        
        except KeyboardInterrupt:
            print("\n👋 Shutting down worker...")
            break
        except Exception as e:
            print(f"❌ Worker error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()

