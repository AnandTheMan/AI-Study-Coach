"""
Setup Script for AI Study Coach
Prepares the environment on a new system
"""
import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("AI Study Coach - System Setup")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    backend_dir = base_dir / "backend"
    frontend_dir = base_dir / "frontend"
    
    # Check Python version
    print("\n✓ Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check for .env file
    print("\n✓ Checking environment configuration...")
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        print("⚠️  Backend .env file not found!")
        print("\nCreating .env file...")
        
        # Get OpenAI API key from user
        api_key = input("\n📝 Enter your OpenAI API Key: ").strip()
        
        if not api_key:
            print("❌ OpenAI API Key is required!")
            sys.exit(1)
        
        # Create .env file
        env_content = f"""# Backend Configuration
OPENAI_API_KEY={api_key}
DATABASE_URL=sqlite:///./oxford_papers.db
SECRET_KEY=your-secret-key-change-in-production-{os.urandom(16).hex()}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
"""
        env_file.write_text(env_content)
        print("✓ Backend .env file created!")
    else:
        # Check if OPENAI_API_KEY exists
        env_content = env_file.read_text()
        if "OPENAI_API_KEY=" not in env_content or "your_openai_api_key_here" in env_content:
            print("⚠️  OPENAI_API_KEY not configured properly!")
            api_key = input("\n📝 Enter your OpenAI API Key: ").strip()
            
            if api_key:
                lines = env_content.split('\n')
                new_lines = []
                found = False
                for line in lines:
                    if line.startswith('OPENAI_API_KEY='):
                        new_lines.append(f'OPENAI_API_KEY={api_key}')
                        found = True
                    else:
                        new_lines.append(line)
                
                if not found:
                    new_lines.insert(0, f'OPENAI_API_KEY={api_key}')
                
                env_file.write_text('\n'.join(new_lines))
                print("✓ OPENAI_API_KEY updated!")
        else:
            print("✓ Backend .env file exists")
    
    # Check frontend .env
    frontend_env = frontend_dir / ".env"
    if not frontend_env.exists():
        print("\n✓ Creating frontend .env file...")
        frontend_env_content = """# Frontend Configuration
API_BASE_URL=http://localhost:8000
"""
        frontend_env.write_text(frontend_env_content)
        print("✓ Frontend .env file created!")
    else:
        print("✓ Frontend .env file exists")
    
    # Check venv
    print("\n✓ Checking virtual environment...")
    venv_dir = base_dir / "venv"
    
    if not venv_dir.exists():
        print("⚠️  Virtual environment not found!")
        print("\nPlease run the following commands:")
        print("\n  python -m venv venv")
        print("  venv\\Scripts\\activate")
        print("  pip install -r requirements.txt")
        print("\nThen run this setup script again.")
        sys.exit(1)
    else:
        print("✓ Virtual environment found")
    
    # Check if database exists
    db_file = backend_dir / "oxford_papers.db"
    if not db_file.exists():
        print("\n✓ Initializing database...")
        try:
            # Import after checking venv
            sys.path.insert(0, str(backend_dir))
            from database import init_db
            init_db()
            print("✓ Database initialized successfully!")
        except Exception as e:
            print(f"⚠️  Could not initialize database: {e}")
            print("The database will be created on first run.")
    else:
        print("✓ Database exists")
    
    # Final instructions
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nTo start the application:")
    print("  python start_app.py")
    print("\nOr manually:")
    print("  Terminal 1: cd backend && python main.py")
    print("  Terminal 2: cd frontend && streamlit run app.py")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
