"""Launcher for the Streamlit app (app.py).

Same idea as ``run_dashboard.py``: Streamlit refuses to start when its port is
already taken and the console window then closes, which looks like a crash.
This launcher picks a free port first and starts Streamlit on it.

Override the first choice with the ``STREAMLIT_PORT`` environment variable.
"""

import os
import socket
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
PREFERRED_PORT = int(os.environ.get("STREAMLIT_PORT", "8501"))
PORT_SCAN_COUNT = 12


def port_is_free(port: int) -> bool:
    """True when nothing is listening on ``port``.

    See run_dashboard.py for why this is not a plain bind(): on Windows
    SO_REUSEADDR lets you bind on top of a server that is already running, so a
    simple bind probe reports busy ports as free. A connect() test catches a
    live listener, and an exclusive bind catches everything else.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.4)
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            return False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def choose_port() -> int:
    if port_is_free(PREFERRED_PORT):
        return PREFERRED_PORT
    for candidate in range(PREFERRED_PORT + 1, PREFERRED_PORT + PORT_SCAN_COUNT):
        if port_is_free(candidate):
            print(f"  Port {PREFERRED_PORT} is already in use "
                  f"-> starting Streamlit on port {candidate} instead.")
            return candidate
    print(f"[ERROR] No free port between {PREFERRED_PORT} and "
          f"{PREFERRED_PORT + PORT_SCAN_COUNT - 1}.")
    return -1


def main() -> int:
    port = choose_port()
    if port < 0:
        input("Press Enter to close...")
        return 1

    print("=" * 66)
    print("  Medicine Price & Alternatives - Streamlit App")
    print("=" * 66)
    print(f"  The app will open in your browser at http://localhost:{port}")
    print("  Press Ctrl+C in this window to stop it.")
    print("=" * 66)

    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(port),
    ]
    try:
        return subprocess.call(cmd, cwd=str(PROJECT_ROOT))
    except KeyboardInterrupt:
        return 0
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[ERROR] Could not start Streamlit: {exc}")
        input("Press Enter to close...")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
