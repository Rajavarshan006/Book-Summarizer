"""
Test script for the Text Summarization API
"""

import requests
import json
import os
from datetime import datetime

# Configurable base URL - can be set via environment variable or use default
BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')

def post_and_validate(endpoint, payload, timeout=30, method='post'):
    """
    Helper function to centralize request, JSON parsing, status checking and key validation

    Args:
        endpoint: API endpoint path
        payload: Data to send
        timeout: Request timeout in seconds
        method: HTTP method ('post' or 'get')

    Returns:
        tuple: (success: bool, result: dict or str, status_code: int)
    """
    url = f"{BASE_URL}{endpoint}"

    try:
        if method.lower() == 'post':
            response = requests.post(url, json=payload, timeout=timeout)
        else:
            response = requests.get(url, timeout=timeout)

        # Check if response status is successful
        if response.status_code != 200:
            return False, f"API returned status {response.status_code}", response.status_code

        # Try to parse JSON response
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError as e:
            return False, f"Invalid JSON response: {str(e)}", response.status_code

        # Validate that result is a dictionary
        if not isinstance(result, dict):
            return False, f"Expected JSON object but got {type(result).__name__}", response.status_code

        return True, result, response.status_code

    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {str(e)}", 0
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", 0

def test_api():
    """Test the API endpoints"""

    # Sample text chunks for testing
    test_chunks = [
        {
            "text": "The quick brown fox jumps over the lazy dog. This sentence contains all the letters in the English alphabet. It's often used for typing practice and testing fonts.",
            "chunk_id": "chunk_1",
            "metadata": {"source": "test"}
        },
        {
            "text": "Artificial intelligence is transforming industries across the globe. From healthcare to finance, AI applications are improving efficiency and accuracy. Machine learning algorithms can analyze vast amounts of data to uncover patterns and insights.",
            "chunk_id": "chunk_2",
            "metadata": {"source": "test"}
        }
    ]

    # Test data
    test_data = {
        "chunks": test_chunks,
        "max_length": 100,
        "min_length": 30
    }

    print("=== Testing Text Summarization API ===")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    print(f"Using BASE_URL: {BASE_URL}")
    print()

    # Test the /summarize endpoint
    print("Testing /summarize endpoint...")
    success, result, status_code = post_and_validate("/summarize", test_data)

    if success:
        # Validate required fields
        if 'summaries' not in result or 'chunk_summaries' not in result:
            print("❌ ERROR: Missing required fields in response")
            return

        print("✅ SUCCESS: API returned valid response")
        print(f"Processing time: {result.get('processing_time', 'N/A')} seconds")
        print(f"Number of summaries: {len(result['summaries'])}")
        print()

        num_summaries = len(result['summaries'])
        num_chunks = len(result['chunk_summaries'])
        for i, summary in enumerate(result['summaries']):
            print(f"Summary {i+1}: {summary}")
            if i < num_chunks:
                print(f"Chunk {i+1} details: {result['chunk_summaries'][i]}")
            print()
    else:
        print(f"❌ ERROR: {result}")

    # Test the /summarize-preprocessed endpoint
    print("\nTesting /summarize-preprocessed endpoint...")
    success, result, status_code = post_and_validate("/summarize-preprocessed", test_data)

    if success:
        # Validate that 'processing_time' exists before accessing it
        if 'processing_time' not in result:
            print("❌ ERROR: Missing 'processing_time' field in response")
        else:
            print("✅ SUCCESS: Preprocessed endpoint returned valid response")
            print(f"Processing time: {result['processing_time']} seconds")
    else:
        print(f"❌ ERROR: {result}")

    # Test health endpoint
    print("\nTesting /health endpoint...")
    success, result, status_code = post_and_validate("/health", None, method='get')

    if success:
        # Validate required fields
        if 'status' not in result or 'service' not in result:
            print("❌ ERROR: Missing required fields in health response")
        else:
            print("✅ SUCCESS: Health check passed")
            print(f"Status: {result['status']}")
            print(f"Service: {result['service']}")
    else:
        print(f"❌ ERROR: {result}")

if __name__ == "__main__":
    test_api()
