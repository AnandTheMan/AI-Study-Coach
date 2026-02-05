"""
Unified Application Launcher
Starts both backend API and frontend Streamlit app together
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    # Get the base directory
    base_dir = Path(__file__).parent
    backend_dir = base_dir / "backend"
    frontend_dir = base_dir / "frontend"
    
    # Python executable from backend venv
    python_exe = backend_dir / "venv" / "Scripts" / "python.exe"
    
    if not python_exe.exists():
        print("❌ Virtual environment not found. Please run setup first.")
        sys.exit(1)
    
    print("🚀 Starting Oxford Examination System...")
    print("=" * 50)
    
    # Start backend server
    print("\n📡 Starting Backend API Server...")
    backend_process = subprocess.Popen(
        [str(python_exe), "main.py"],
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Check if backend is running
    if backend_process.poll() is not None:
        print("❌ Backend failed to start!")
        stderr = backend_process.stderr.read()
        print(stderr)
        sys.exit(1)
    
    print("✅ Backend API running on http://localhost:8000")
    
    # Start frontend server
    print("\n🎨 Starting Frontend Streamlit App...")
    frontend_process = subprocess.Popen(
        [str(python_exe), "-m", "streamlit", "run", "app.py"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Wait for frontend to start
    time.sleep(5)
    
    print("✅ Frontend running on http://localhost:8501")
    print("\n" + "=" * 50)
    print("🎉 Application is ready!")
    print("📱 Open http://localhost:8501 in your browser")
    print("\n💡 Press Ctrl+C to stop both servers")
    print("=" * 50)
    
    try:
        # Keep both processes running
        while True:
            # Check if backend is still running
            if backend_process.poll() is not None:
                print("\n❌ Backend stopped unexpectedly!")
                break
            
            # Check if frontend is still running
            if frontend_process.poll() is not None:
                print("\n❌ Frontend stopped unexpectedly!")
                break
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        
        # Terminate both processes
        print("⏹️  Stopping frontend...")
        frontend_process.terminate()
        
        print("⏹️  Stopping backend...")
        backend_process.terminate()
        
        # Wait for clean shutdown
        time.sleep(2)
        
        # Force kill if still running
        try:
            frontend_process.kill()
            backend_process.kill()
        except:
            pass
        
        print("✅ Application stopped successfully!")
    
    finally:
        # Ensure processes are terminated
        try:
            frontend_process.terminate()
            backend_process.terminate()
        except:
            pass

if __name__ == "__main__":
    main()
