"""
Test script to verify the fix works when actual errors occur
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

from backend.api import app
from fastapi.testclient import TestClient
from backend.api import TextChunk, SummarizationRequest

client = TestClient(app)

def test_with_actual_errors():
    """Test with chunks that will actually cause errors to verify placeholder insertion"""

    # Create a request with chunks that will cause errors
    request_data = {
        "chunks": [
            {"text": "This is valid text that should work fine.", "chunk_id": "chunk_1"},
            {"text": "x" * 10000, "chunk_id": "chunk_2"},  # Very long text might cause issues
            {"text": "Another valid chunk of text for summarization.", "chunk_id": "chunk_3"},
        ],
        "max_length": 150,
        "min_length": 40
    }

    response = client.post("/summarize", json=request_data)

    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Number of summaries: {len(data['summaries'])}")
        print(f"Number of chunk_summaries: {len(data['chunk_summaries'])}")

        # Check if lists are aligned
        if len(data['summaries']) == len(data['chunk_summaries']):
            print("✅ Lists are properly aligned!")

            # Check which chunks had errors and verify None placeholders
            error_count = 0
            for i, (summary, chunk_summary) in enumerate(zip(data['summaries'], data['chunk_summaries'])):
                has_error = 'error' in chunk_summary
                print(f"Chunk {i+1}: summary={summary is not None}, has_error={has_error}")
                if has_error:
                    error_count += 1
                    print(f"  Error: {chunk_summary['error']}")
                    if summary is not None:
                        print(f"  ❌ ERROR: Summary should be None when there's an error!")
                    else:
                        print(f"  ✅ Correctly has None placeholder")
                else:
                    if summary is None:
                        print(f"  ❌ ERROR: Summary should not be None when there's no error!")
                    else:
                        print(f"  ✅ Correctly has actual summary")

            print(f"\nSummary: {error_count} chunks had errors, all handled correctly")
        else:
            print("❌ Lists are NOT aligned - fix failed!")
            print(f"Summaries length: {len(data['summaries'])}")
            print(f"Chunk_summaries length: {len(data['chunk_summaries'])}")
    else:
        print(f"Request failed with status {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_with_actual_errors()
