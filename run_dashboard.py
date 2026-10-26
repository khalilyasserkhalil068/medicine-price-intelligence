"""Launcher for the Flask dashboard (dashboard/app.py).

Why this file exists instead of starting Flask directly
-------------------------------------------------------
Port 5000 is one of the most commonly taken ports on a Windows machine. When it
is already occupied, ``app.run()`` dies with::

    OSError: [WinError 10048] Only one usage of each socket address ...

and the console window flashes and closes, which looks exactly like
"the dashboard is broken". This launcher instead:

1. checks the preferred port (``DASHBOARD_PORT`` env var, default 5000),
2. tells you if a *previous copy of this same dashboard* is still running there,
   because that old process keeps serving its in-memory templates,
3. otherwise moves on to the next free port automatically,
4. opens the browser at whatever port was actually used.

Ctrl+C in the console stops the server.
"""

import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "dashboard"))

from app import app  # noqa: E402  (path set up above)

PREFERRED_PORT = int(os.environ.get("DASHBOARD_PORT", "5000"))
PORT_SCAN_COUNT = 12
HOST = "0.0.0.0"


def port_is_free(port: int) -> bool:
    """True when nothing is listening on ``port``.

    WINDOWS GOTCHA - do not "simplify" this back to a plain bind():
    ``SO_REUSEADDR`` means *allow binding to an address that is already in use*
    on Windows (it does the opposite of what the name suggests, unlike Linux).
    Probe-binding with SO_REUSEADDR therefore reports a busy port as free, and
    Werkzeug then happily binds on top of the running server - requests get
    answered by the OLD process, so the app silently keeps serving stale code.

    Two independent checks are used instead:
      1. a TCP connect() - if anything answers, the port is taken;
      2. an exclusive bind (SO_EXCLUSIVEADDRUSE on Windows) for the rest.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.4)
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            return False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            # Windows-only: guarantees the bind fails if the port is taken.
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def looks_like_this_dashboard(port: int) -> bool:
    """True when ``port`` already answers with this dashboard's own API."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/kpi", timeout=1.5) as resp:
            body = resp.read(400).decode("utf-8", "replace")
    except Exception:
        return False
    return '"total_medicines"' in body


def pid_listening_on(port: int):
    """Best-effort PID of the process listening on ``port`` (for the message)."""
    try:
        out = subprocess.run(
            ["netstat", "-ano", "-p", "TCP"],
            capture_output=True, text=True, timeout=10,
        ).stdout
    except Exception:
        return None
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[3] == "LISTENING" and parts[1].endswith(f":{port}"):
            try:
                return int(parts[4])
            except ValueError:
                return None
    return None


def choose_port() -> tuple[int, list[str]]:
    """Return (port, notes). Picks the preferred port, or the next free one."""
    notes: list[str] = []
    if port_is_free(PREFERRED_PORT):
        return PREFERRED_PORT, notes

    if looks_like_this_dashboard(PREFERRED_PORT):
        pid = pid_listening_on(PREFERRED_PORT)
        notes.append(
            f"An OLDER copy of this dashboard is still running on port {PREFERRED_PORT}"
            + (f" (pid {pid})" if pid else "")
            + "."
        )
        notes.append(
            "That older server keeps its own copy of the pages in memory, so it will"
        )
        notes.append(
            "NOT show the latest changes. Close that console window (or run"
        )
        notes.append(
            f"   taskkill /PID {pid} /F" if pid else "   taskkill /F /IM python.exe"
        )
        notes.append("in a terminal) to free port 5000 again.")
    else:
        notes.append(f"Port {PREFERRED_PORT} is already used by another program.")

    for candidate in range(PREFERRED_PORT + 1, PREFERRED_PORT + PORT_SCAN_COUNT):
        if port_is_free(candidate):
            notes.append(f"-> Starting on port {candidate} instead. Nothing is blocked.")
            return candidate, notes

    notes.append(
        f"[ERROR] No free port found between {PREFERRED_PORT} and "
        f"{PREFERRED_PORT + PORT_SCAN_COUNT - 1}."
    )
    return -1, notes


def open_browser_later(url: str) -> None:
    def worker() -> None:
        time.sleep(1.6)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=worker, daemon=True).start()


def main() -> int:
    port, notes = choose_port()

    print("=" * 66)
    print("  Medicine Price & Alternatives Dashboard (Flask)")
    print("=" * 66)
    for note in notes:
        print("  " + note)
    if port < 0:
        print()
        input("Press Enter to close...")
        return 1

    url = f"http://localhost:{port}"
    print()
    print(f"  Server running at: {url}")
    print("  Press Ctrl+C in this window to stop.")
    print("=" * 66)

    open_browser_later(url)
    try:
        app.run(host=HOST, port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        pass
    except OSError as exc:
        print()
        print(f"[ERROR] Could not start the server on port {port}: {exc}")
        print("        Another program may have taken the port just now.")
        input("Press Enter to close...")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
