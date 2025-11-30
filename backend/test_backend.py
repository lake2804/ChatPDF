"""
Quick test script to verify backend functionality.
"""
import sys
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload():
    """Test upload endpoint."""
    print("\nTesting /upload endpoint...")
    
    # Create a test text file
    test_file_path = Path("test_upload.txt")
    try:
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("This is a test document for the RAG system.\n")
            f.write("It contains some sample text to test the upload and indexing functionality.\n")
            f.write("The system should be able to process this and make it searchable.")
        
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_upload.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/upload", files=files, timeout=30)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Clean up test file
        if test_file_path.exists():
            test_file_path.unlink()

def test_ask():
    """Test ask endpoint."""
    print("\nTesting /ask endpoint...")
    try:
        data = {
            "question": "What is this document about?",
            "k": 3
        }
        response = requests.post(
            f"{BASE_URL}/ask",
            json=data,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result.get('answer', 'N/A')[:200]}...")
            print(f"Sources: {result.get('source_count', 0)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 50)
    print("Backend Test Suite")
    print("=" * 50)
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health()))
    
    # Test upload
    results.append(("Upload", test_upload()))
    
    # Test ask
    results.append(("Ask Question", test_ask()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

