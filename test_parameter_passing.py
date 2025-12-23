#!/usr/bin/env python3

"""
Test script to verify that the parameters are correctly passed from frontend to backend.
This tests the function signature without requiring all dependencies.
"""

import ast
import inspect

def test_function_signature():
    """Test that the summarize_book function has the correct parameters."""

    # Read the backend service file
    with open('backend/book_summarization_service.py', 'r') as f:
        content = f.read()

    # Parse the file to find the function definition
    tree = ast.parse(content)

    # Find the summarize_book function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'summarize_book':
            # Extract parameter names
            params = []
            for arg in node.args.args:
                params.append(arg.arg)

            # Check if all required parameters are present
            required_params = ['book_id', 'user_id', 'summary_length', 'summary_style', 'chunk_size', 'overlap_percentage']
            missing_params = [param for param in required_params if param not in params]

            if missing_params:
                print(f"❌ Missing parameters: {missing_params}")
                return False
            else:
                print(f"✅ All required parameters found: {params[:6]}")
                return True

    print("❌ summarize_book function not found")
    return False

def test_frontend_call():
    """Test that the frontend calls the function with all parameters."""

    # Read the frontend file
    with open('frontend/generate_summary.py', 'r') as f:
        content = f.read()

    # Check if the call includes all parameters
    if 'summarize_book(' in content:
        # Find the call
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'summarize_book(' in line:
                # Collect the full call (may span multiple lines)
                call_lines = [line]
                j = i + 1
                while j < len(lines) and ')' not in lines[j]:
                    call_lines.append(lines[j])
                    j += 1
                if j < len(lines):
                    call_lines.append(lines[j])

                full_call = '\n'.join(call_lines)
                print(f"Found call:\n{full_call}")

                # Check for parameter names
                required_params = ['summary_length', 'summary_style', 'chunk_size', 'overlap_percentage']
                missing_in_call = []

                for param in required_params:
                    if param not in full_call:
                        missing_in_call.append(param)

                if missing_in_call:
                    print(f"❌ Missing parameters in call: {missing_in_call}")
                    return False
                else:
                    print("✅ All parameters are passed in the frontend call")
                    return True

    print("❌ summarize_book call not found in frontend")
    return False

if __name__ == "__main__":
    print("Testing parameter passing implementation...")
    print("\n1. Testing backend function signature:")
    backend_ok = test_function_signature()

    print("\n2. Testing frontend function call:")
    frontend_ok = test_frontend_call()

    if backend_ok and frontend_ok:
        print("\n🎉 All tests passed! Parameters are correctly implemented.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
