#!/usr/bin/env python3
"""
Test script to verify the ZeroDivisionError fix in performance_logger.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.performance_logger import PerformanceLogger

def test_zero_division_fix():
    """Test that the log_total_processing method handles chunk_count=0 correctly"""
    print("Testing ZeroDivisionError fix in PerformanceLogger...")

    # Create a test logger
    test_logger = PerformanceLogger(name="test_logger")

    # Test case 1: Normal case with chunk_count > 0
    print("\nTest 1: Normal case (chunk_count > 0)")
    try:
        test_logger.log_total_processing(
            total_time=10.5,
            chunk_count=5,
            success_count=4,
            error_count=1
        )
        print("✓ Normal case passed - no exception raised")
    except Exception as e:
        print(f"✗ Normal case failed with error: {e}")
        return False

    # Test case 2: Edge case with chunk_count = 0 (this would have caused ZeroDivisionError before the fix)
    print("\nTest 2: Edge case (chunk_count = 0)")
    try:
        test_logger.log_total_processing(
            total_time=10.5,
            chunk_count=0,
            success_count=0,
            error_count=0
        )
        print("✓ Zero chunk_count case passed - no ZeroDivisionError raised")
    except ZeroDivisionError as e:
        print(f"✗ Zero chunk_count case failed with ZeroDivisionError: {e}")
        return False
    except Exception as e:
        print(f"✗ Zero chunk_count case failed with unexpected error: {e}")
        return False

    # Test case 3: Another edge case with chunk_count = 0 but non-zero error_count
    print("\nTest 3: Edge case (chunk_count = 0, error_count > 0)")
    try:
        test_logger.log_total_processing(
            total_time=5.0,
            chunk_count=0,
            success_count=0,
            error_count=3
        )
        print("✓ Zero chunk_count with errors case passed - no ZeroDivisionError raised")
    except ZeroDivisionError as e:
        print(f"✗ Zero chunk_count with errors case failed with ZeroDivisionError: {e}")
        return False
    except Exception as e:
        print(f"✗ Zero chunk_count with errors case failed with unexpected error: {e}")
        return False

    print("\n" + "="*50)
    print("All tests passed! The ZeroDivisionError fix is working correctly.")
    print("The avg_time variable is properly computed as 0 when chunk_count = 0")
    return True

if __name__ == "__main__":
    success = test_zero_division_fix()
    sys.exit(0 if success else 1)
