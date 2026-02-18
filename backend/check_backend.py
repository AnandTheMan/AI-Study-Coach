"""
Backend Diagnostics and Setup Verification
Run this to check if backend is ready to start
"""
import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("\n1. Checking Python Version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"   ❌ Python {version.major}.{version.minor} - Need Python 3.8+")
        return False
    print(f"   ✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n2. Checking Dependencies...")
    required = [
        'fastapi', 'uvicorn', 'openai', 'sqlalchemy', 
        'pydantic', 'python-dotenv', 'passlib', 'python-jose'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n   Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check .env file configuration"""
    print("\n3. Checking Environment Configuration...")
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print(f"   ❌ .env file not found!")
        print(f"   Create: {env_file}")
        return False
    
    print(f"   ✓ .env file exists")
    
    # Read and check contents
    env_content = env_file.read_text()
    
    if "OPENAI_API_KEY" not in env_content:
        print(f"   ❌ OPENAI_API_KEY not in .env")
        return False
    
    if "your_openai_api_key_here" in env_content:
        print(f"   ❌ OPENAI_API_KEY not configured (still has placeholder)")
        return False
    
    # Check if it starts with sk-
    for line in env_content.split('\n'):
        if line.startswith('OPENAI_API_KEY='):
            key = line.split('=', 1)[1].strip()
            if key and key.startswith('sk-'):
                print(f"   ✓ OPENAI_API_KEY configured")
            else:
                print(f"   ⚠️  OPENAI_API_KEY might be invalid (should start with 'sk-')")
            break
    
    return True

def check_database():
    """Check database setup"""
    print("\n4. Checking Database...")
    try:
        from database import init_db, get_db
        db_file = Path(__file__).parent / "oxford_papers.db"
        
        if db_file.exists():
            print(f"   ✓ Database file exists")
        else:
            print(f"   ⚠️  Database will be created on first run")
        
        # Try to initialize
        init_db()
        print(f"   ✓ Database schema ready")
        return True
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def check_port():
    """Check if port 8000 is available"""
    print("\n5. Checking Port Availability...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result == 0:
        print(f"   ⚠️  Port 8000 is already in use!")
        print(f"      Another process might be running on this port")
        print(f"      Stop it or use a different port")
        return False
    else:
        print(f"   ✓ Port 8000 is available")
        return True

def test_imports():
    """Test critical imports"""
    print("\n6. Testing Critical Imports...")
    try:
        import config
        print(f"   ✓ config")
        
        import database
        print(f"   ✓ database")
        
        import openai_service
        print(f"   ✓ openai_service")
        
        import auth
        print(f"   ✓ auth")
        
        return True
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

def main():
    print("=" * 60)
    print("Backend Diagnostics - AI Study Coach")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_env_file(),
        test_imports(),
        check_database(),
        check_port()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ ALL CHECKS PASSED!")
        print("=" * 60)
        print("\nBackend is ready to start!")
        print("Run: python main.py")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("=" * 60)
        print("\nPlease fix the issues above before starting backend.")
        print("\nQuick fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Configure .env: Copy .env.example and add your OpenAI API key")
        print("  • Get API key: https://platform.openai.com/api-keys")
    print()

if __name__ == "__main__":
    main()
