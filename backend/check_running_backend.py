"""
Check which Python environment the running backend is using.
"""
import sys
import subprocess
import requests
import json

def check_backend_environment():
    """Check backend environment info."""
    try:
        # Try to get info from a custom endpoint (we'll add this)
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.ok:
            print("✅ Backend is running")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"⚠️  Backend responded with status {response.status}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False
    
    print("\n" + "="*50)
    print("Current Python Environment (this script):")
    print("="*50)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Check pypdf in current environment
    try:
        import pypdf
        print(f"✅ pypdf is available: {pypdf.__version__}")
        print(f"   Location: {pypdf.__file__}")
    except ImportError:
        print("❌ pypdf is NOT available in current environment")
        print("   Install with: pip install pypdf")
    
    print("\n" + "="*50)
    print("Recommendation:")
    print("="*50)
    print("1. Make sure backend is running with the same Python environment")
    print("2. If using virtual environment, activate it before starting backend:")
    print("   - Windows: venv\\Scripts\\activate")
    print("   - Linux/Mac: source venv/bin/activate")
    print("3. Then start backend: uvicorn app.api:app --reload")
    
    return True

if __name__ == "__main__":
    check_backend_environment()

