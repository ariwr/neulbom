import sys
import os

print(f"Python executable: {sys.executable}")
print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    import fastapi
    print("[OK] fastapi imported")
except ImportError as e:
    print(f"[FAIL] fastapi import failed: {e}")

try:
    import uvicorn
    print("[OK] uvicorn imported")
except ImportError as e:
    print(f"[FAIL] uvicorn import failed: {e}")

try:
    from app.main import app
    print("[OK] app.main imported successfully")
except ImportError as e:
    print(f"[FAIL] app.main import failed: {e}")
except Exception as e:
    print(f"[FAIL] app.main crashed: {e}")

print("Diagnostic complete")

