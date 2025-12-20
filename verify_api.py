"""
Simple verification script for the API
"""

import requests
import json

def verify_api():
    """Verify the API is working correctly"""

    # Simple test chunk
    test_chunk = {
        "chunks": [
            {
                "text": "This is a test sentence to verify the API functionality. The API should accept this text and return a summary.",
                "chunk_id": "test_chunk"
            }
        ]
    }

    try:
        print("🔍 Verifying API endpoints...")

        # Test health endpoint
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            print("✅ Health endpoint: OK")
        else:
            print("❌ Health endpoint: FAILED")

        # Test summarization endpoint
        summary_response = requests.post(
            "http://localhost:8000/summarize",
            json=test_chunk,
            timeout=30
        )

        if summary_response.status_code == 200:
            result = summary_response.json()
            print("✅ Summarization endpoint: OK")
            print(f"   Summary: {result['summaries'][0][:100]}...")
            print(f"   Processing time: {result['processing_time']}s")
        else:
            print("❌ Summarization endpoint: FAILED")

        print("\n🎉 API verification complete!")

    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")

if __name__ == "__main__":
    verify_api()
