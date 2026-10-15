"""Start the LegalEase frontend and backend together after setup."""

from pathlib import Path
import os
import signal
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent


def main() -> None:
    npm = "npm.cmd" if os.name == "nt" else "npm"
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT,
    )
    frontend = subprocess.Popen([npm, "run", "dev"], cwd=ROOT)
    print("\nLegalEase is starting at http://localhost:5173")
    print("Press Ctrl+C to stop both services.\n")
    try:
        while backend.poll() is None and frontend.poll() is None:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for process in (frontend, backend):
            if process.poll() is None:
                process.send_signal(signal.SIGTERM if os.name != "nt" else signal.CTRL_BREAK_EVENT)
        for process in (frontend, backend):
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()


if __name__ == "__main__":
    main()
