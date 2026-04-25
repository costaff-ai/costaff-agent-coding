"""
Process management tools — start and stop background processes, wait for ports.
Designed for integration testing: start a server, test it, then stop it.
"""
import json
import os
import signal
import socket
import subprocess
import time

from _shared import _workspace


def _registry_path():
    return _workspace() / ".process_registry.json"


def _load() -> dict:
    p = _registry_path()
    try:
        return json.loads(p.read_text()) if p.exists() else {}
    except Exception:
        return {}


def _save(reg: dict) -> None:
    _registry_path().write_text(json.dumps(reg, indent=2))


def start_process(command: str, name: str) -> str:
    """
    Start a shell command as a named background process.
    Use wait_for_port() afterwards to confirm the server is ready before testing.
    command: shell command to run (executed inside the workspace directory).
    name: short identifier for this process (used with stop_process).
    """
    reg = _load()
    if name in reg:
        pid = reg[name]["pid"]
        try:
            os.kill(pid, 0)
            return f"[ERROR]: Process '{name}' (pid {pid}) is already running. Use stop_process() first."
        except ProcessLookupError:
            pass  # stale entry — overwrite

    try:
        proc = subprocess.Popen(
            command,
            shell=True,
            cwd=str(_workspace()),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        reg[name] = {"pid": proc.pid, "command": command}
        _save(reg)
        return f"Started '{name}' (pid {proc.pid}): {command}"
    except Exception as e:
        return f"[ERROR]: {e}"


def wait_for_port(port: int, timeout: int = 15) -> str:
    """
    Block until a TCP port on localhost accepts connections (or timeout expires).
    Call after start_process() to wait for a web server to become ready.
    port: TCP port number to poll (1–65535).
    timeout: maximum seconds to wait (default: 15).
    """
    if not (1 <= port <= 65535):
        return "[ERROR]: port must be between 1 and 65535."
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                elapsed = round(time.time() - start, 1)
                return f"Port {port} ready (after {elapsed}s)."
        except (ConnectionRefusedError, OSError):
            time.sleep(0.25)
    return f"[ERROR]: Port {port} not ready after {timeout}s."


def stop_process(name: str) -> str:
    """
    Stop a named background process that was started with start_process().
    Sends SIGTERM to the entire process group.
    name: the identifier used when starting the process.
    """
    reg = _load()
    if name not in reg:
        return f"[ERROR]: No process named '{name}'. Use list_processes() to see registered processes."
    pid = reg[name]["pid"]
    try:
        os.killpg(pid, signal.SIGTERM)
        del reg[name]
        _save(reg)
        return f"Stopped '{name}' (pid {pid})."
    except ProcessLookupError:
        del reg[name]
        _save(reg)
        return f"Process '{name}' (pid {pid}) was already dead (stale entry removed)."
    except Exception as e:
        return f"[ERROR]: {e}"


def list_processes() -> str:
    """
    List all background processes registered by start_process() and their current status.
    Automatically cleans up stale (dead) entries from the registry.
    """
    reg = _load()
    if not reg:
        return "(no background processes registered)"

    lines = []
    stale = []
    for name, info in sorted(reg.items()):
        pid = info["pid"]
        try:
            os.kill(pid, 0)
            status = "running"
        except ProcessLookupError:
            status = "dead"
            stale.append(name)
        lines.append(f"  {name:<20} pid={pid:<8} [{status}]  {info['command']}")

    if stale:
        for n in stale:
            del reg[n]
        _save(reg)

    return "── Background processes ──\n" + "\n".join(lines)
