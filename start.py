import subprocess
import sys
import time
import os

def print_banner():
    banner = """
    ========================================================
    🚀 Welcome to AskDB - AI Database Assistant! 🚀
    ========================================================
    Starting services...

    🔗 Frontend (Streamlit): http://localhost:8501
    🔗 Backend (FastAPI):    http://localhost:8000
    📜 API Docs (Swagger):   http://localhost:8000/docs
    ========================================================
    """
    print(banner)

def start_services():
    print_banner()

    python_exec = sys.executable

    try:
        print("Starting FastAPI Backend...")
        backend_process = subprocess.Popen(
            [python_exec, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        print("Starting Streamlit Frontend...")
        frontend_process = subprocess.Popen(
            [python_exec, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Services stopped successfully.")
        sys.exit(0)

if __name__ == "__main__":
    start_services()
