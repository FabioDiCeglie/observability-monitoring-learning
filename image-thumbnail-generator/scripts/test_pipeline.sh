#!/bin/bash

set -e

API_URL="http://localhost:8000"
TEST_IMAGE="${1:-storage/uploads/1cfede2e-780d-481c-af22-64835f0af15e.jpg}"
OUTPUT_DIR="test_results"

echo "🧪 Testing Image Thumbnail Generator Pipeline"
echo "=============================================="
echo ""

# Check if test image exists
if [ ! -f "$TEST_IMAGE" ]; then
    echo "❌ Test image not found: $TEST_IMAGE"
    echo "Usage: $0 [path/to/image.jpg]"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"
echo "📁 Output directory: $OUTPUT_DIR"
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Check..."
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
echo "   Response: $HEALTH_RESPONSE"
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed"
    exit 1
fi
echo ""

# Test 2: Upload Image
echo "2️⃣  Uploading image..."
UPLOAD_RESPONSE=$(curl -s -X POST "$API_URL/api/images" \
    -F "file=@$TEST_IMAGE")

echo "   Response: $UPLOAD_RESPONSE"

# Extract image ID from response
IMAGE_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$IMAGE_ID" ]; then
    echo "   ❌ Failed to upload image"
    exit 1
fi

echo "   ✅ Image uploaded successfully"
echo "   📋 Image ID: $IMAGE_ID"
echo ""

# Test 3: Wait for Processing
echo "3️⃣  Waiting for image processing..."
MAX_WAIT=30
WAIT_TIME=0

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    sleep 2
    WAIT_TIME=$((WAIT_TIME + 2))
    echo "   ⏳ Waiting... ${WAIT_TIME}s"
    
    # Try to download small thumbnail to check if processing is done
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/images/$IMAGE_ID/small")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ Processing completed in ${WAIT_TIME}s"
        break
    fi
    
    if [ $WAIT_TIME -ge $MAX_WAIT ]; then
        echo "   ⚠️  Processing timeout (${MAX_WAIT}s)"
        echo "   Check worker logs: docker logs image-worker"
        exit 1
    fi
done
echo ""

# Test 4: Download Thumbnails
echo "4️⃣  Downloading thumbnails..."

for SIZE in small medium large; do
    OUTPUT_FILE="$OUTPUT_DIR/${IMAGE_ID}_${SIZE}.jpg"
    
    echo "   📥 Downloading $SIZE thumbnail..."
    HTTP_CODE=$(curl -s -o "$OUTPUT_FILE" -w "%{http_code}" "$API_URL/api/images/$IMAGE_ID/$SIZE")
    
    if [ "$HTTP_CODE" = "200" ]; then
        FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
        DIMENSIONS=$(file "$OUTPUT_FILE" | grep -o '[0-9]*x[0-9]*' | head -1)
        echo "      ✅ $SIZE: $DIMENSIONS ($FILE_SIZE)"
    else
        echo "      ❌ Failed to download $SIZE (HTTP $HTTP_CODE)"
    fi
done
echo ""

# Test 5: Summary
echo "5️⃣  Test Summary"
echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Image ID: $IMAGE_ID"
echo "   Thumbnails saved to: $OUTPUT_DIR/"
echo ""
ls -lh "$OUTPUT_DIR"/${IMAGE_ID}_*.jpg 2>/dev/null || echo "   No thumbnails found"
echo ""
echo "✅ Pipeline test completed successfully!"
echo ""
echo "📊 To view worker logs:"
echo "   docker logs image-worker --tail 50"
echo ""
echo "🧹 To clean up test results:"
echo "   rm -rf $OUTPUT_DIR"

