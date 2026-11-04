"""
Sneaker Squad - 1-Click Server Runner
Click the Play (▶️) button in the top-right corner of your editor to start the server!
Or run in terminal: python run.py
"""
import os
import sys
import socket
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def main():
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    os.chdir(str(BASE_DIR))
    local_ip = get_local_ip()

    print("=" * 60)
    print("           STARTING SNEAKER SQUAD SERVER")
    print("=" * 60)
    print(f"  Laptop / PC URL:   http://127.0.0.1:8000/")
    print(f"  Mobile Phone URL:  http://{local_ip}:8000/")
    print(f"  Admin Portal URL:  http://127.0.0.1:8000/admin/")
    print(f"  Admin Username:    admin")
    print(f"  Admin Password:    admin123")
    print("=" * 60)
    print("\nStarting Django Server on 0.0.0.0:8000 (Accessible from Phone and PC)...\n")

    venv_python = BASE_DIR / 'venv' / 'Scripts' / 'python.exe'
    python_bin = str(venv_python) if venv_python.exists() else sys.executable

    manage_py = BASE_DIR / 'manage.py'
    cmd = [python_bin, str(manage_py), 'runserver', '0.0.0.0:8000']
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[INFO] Sneaker Squad Server stopped.")

if __name__ == '__main__':
    main()
