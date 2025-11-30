"""
Check if all imports work correctly.
"""
import sys

def check_import(module_name, description):
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {description}: OK")
        return True
    except ImportError as e:
        print(f"❌ {description}: FAILED - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {description}: WARNING - {e}")
        return False

def main():
    print("Checking backend imports...")
    print("=" * 50)
    
    results = []
    
    # Core Python modules
    results.append(check_import("os", "os module"))
    results.append(check_import("pathlib", "pathlib module"))
    results.append(check_import("logging", "logging module"))
    results.append(check_import("typing", "typing module"))
    
    # FastAPI
    results.append(check_import("fastapi", "FastAPI"))
    results.append(check_import("uvicorn", "Uvicorn"))
    
    # LangChain
    results.append(check_import("langchain_core", "LangChain Core"))
    results.append(check_import("langchain_community", "LangChain Community"))
    results.append(check_import("langchain_google_genai", "LangChain Google GenAI"))
    
    # Google AI
    results.append(check_import("google.genai", "Google GenAI"))
    
    # Qdrant
    results.append(check_import("qdrant_client", "Qdrant Client"))
    
    # Document processing
    results.append(check_import("PIL", "Pillow (PIL)"))
    
    # Try importing app modules
    print("\nChecking app modules...")
    print("=" * 50)
    
    try:
        from app import config
        print("✅ app.config: OK")
        results.append(True)
    except Exception as e:
        print(f"❌ app.config: FAILED - {e}")
        results.append(False)
    
    try:
        from app import embeddings
        print("✅ app.embeddings: OK")
        results.append(True)
    except Exception as e:
        print(f"❌ app.embeddings: FAILED - {e}")
        results.append(False)
    
    try:
        from app import store
        print("✅ app.store: OK")
        results.append(True)
    except Exception as e:
        print(f"❌ app.store: FAILED - {e}")
        results.append(False)
    
    try:
        from app import loader
        print("✅ app.loader: OK")
        results.append(True)
    except Exception as e:
        print(f"❌ app.loader: FAILED - {e}")
        results.append(False)
    
    try:
        from app import vision
        print("✅ app.vision: OK")
        results.append(True)
    except Exception as e:
        print(f"❌ app.vision: FAILED - {e}")
        results.append(False)
    
    try:
        from app import rag
        print("✅ app.rag: OK")
        results.append(True)
    except Exception as e:
        print(f"❌ app.rag: FAILED - {e}")
        results.append(False)
    
    try:
        from app import api
        print("✅ app.api: OK")
        results.append(True)
    except Exception as e:
        print(f"❌ app.api: FAILED - {e}")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All imports successful!")
        return 0
    else:
        print("❌ Some imports failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

