"""
Check if all required dependencies are installed in the current environment.
"""
import sys
import subprocess

def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name}: OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: MISSING - {e}")
        return False

def main():
    print("Checking backend dependencies...")
    print("=" * 50)
    
    results = []
    
    # Critical packages
    results.append(check_package("pypdf", "pypdf"))
    results.append(check_package("pymupdf", "fitz"))
    results.append(check_package("langchain_community", "langchain_community"))
    results.append(check_package("langchain_google_genai", "langchain_google_genai"))
    results.append(check_package("qdrant_client", "qdrant_client"))
    results.append(check_package("google.genai", "google.genai"))
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed < total:
        print("\n⚠️  Some packages are missing!")
        print("Please run: pip install -r requirements.txt")
        return 1
    else:
        print("✅ All dependencies are installed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

