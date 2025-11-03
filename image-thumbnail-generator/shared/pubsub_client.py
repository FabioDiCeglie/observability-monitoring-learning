"""
Google Pub/Sub client wrapper for message publishing and consuming.
"""
import os
import json
from typing import Dict, Any, Optional
from google.cloud import pubsub_v1
from shared.config import Config


class PubSubClient:
    """Wrapper for Google Pub/Sub operations."""
    
    def __init__(self):
        """Initialize Pub/Sub client with emulator support."""
        # Set emulator host for local development
        os.environ["PUBSUB_EMULATOR_HOST"] = Config.PUBSUB_EMULATOR_HOST
        
        self.project_id = Config.PUBSUB_PROJECT_ID
        self.topic_name = Config.PUBSUB_TOPIC
        
        # Initialize publisher and subscriber
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        
        # Topic and subscription paths
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
        self.subscription_name = f"{self.topic_name}-subscription"
        self.subscription_path = self.subscriber.subscription_path(self.project_id, self.subscription_name)
        
        print(f"📡 Pub/Sub initialized: {self.topic_path}")
    
    def create_topic_if_not_exists(self):
        """Create topic and subscription if they don't exist."""
        try:
            # Try to create topic
            self.publisher.create_topic(request={"name": self.topic_path})
            print(f"✅ Created topic: {self.topic_name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️  Topic already exists: {self.topic_name}")
            else:
                print(f"⚠️  Error creating topic: {e}")
        
        try:
            # Try to create subscription
            self.subscriber.create_subscription(
                request={
                    "name": self.subscription_path,
                    "topic": self.topic_path,
                    "ack_deadline_seconds": 60
                }
            )
            print(f"✅ Created subscription: {self.subscription_name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️  Subscription already exists: {self.subscription_name}")
            else:
                print(f"⚠️  Error creating subscription: {e}")
    
    def publish_message(self, message: Dict[str, Any]) -> str:
        """
        Publish a message to the topic.
        
        Args:
            message: Dictionary to publish as JSON
            
        Returns:
            Message ID from Pub/Sub
        """
        # Convert message to JSON bytes
        data = json.dumps(message).encode("utf-8")
        
        # Publish message
        future = self.publisher.publish(self.topic_path, data)
        message_id = future.result()
        
        print(f"📤 Published message: {message_id}")
        return message_id
    
    def pull_messages(self, max_messages: int = 1, timeout: float = 5.0):
        """
        Pull messages from subscription (synchronous).
        
        Args:
            max_messages: Maximum number of messages to pull
            timeout: Timeout in seconds
            
        Returns:
            List of received messages
        """
        try:
            response = self.subscriber.pull(
                request={
                    "subscription": self.subscription_path,
                    "max_messages": max_messages,
                },
                timeout=timeout,
            )
            
            return response.received_messages
        except Exception as e:
            # Timeout or no messages is normal
            return []
    
    def acknowledge_message(self, ack_id: str):
        """
        Acknowledge a message (removes it from queue).
        
        Args:
            ack_id: Acknowledgment ID from received message
        """
        self.subscriber.acknowledge(
            request={
                "subscription": self.subscription_path,
                "ack_ids": [ack_id],
            }
        )
        print(f"✅ Acknowledged message")
    
    def nack_message(self, ack_id: str):
        """
        Negative acknowledge a message (requeue for retry).
        
        Args:
            ack_id: Acknowledgment ID from received message
        """
        self.subscriber.modify_ack_deadline(
            request={
                "subscription": self.subscription_path,
                "ack_ids": [ack_id],
                "ack_deadline_seconds": 0,  # Requeue immediately
            }
        )
        print(f"↩️  Requeued message for retry")


# Singleton instance
_pubsub_client: Optional[PubSubClient] = None


def get_pubsub_client() -> PubSubClient:
    """Get or create the Pub/Sub client singleton."""
    global _pubsub_client
    if _pubsub_client is None:
        _pubsub_client = PubSubClient()
        _pubsub_client.create_topic_if_not_exists()
    return _pubsub_client

