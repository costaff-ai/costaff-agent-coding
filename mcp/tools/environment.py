"""
Environment tools — manage packages and inspect the Python runtime.
"""
import subprocess
import sys
from pathlib import Path

from _shared import _packages_dir, _workspace, TIMEOUT_SHORT, TIMEOUT_INSTALL


def pip_install(package: str) -> str:
    """
    Install a Python package (or packages) using pip.
    Packages are installed to a persistent directory and survive container restarts.
    package: package name or spec (e.g. 'pandas', 'numpy==1.26', 'scikit-learn pandas').
    """
    if os.getenv("ALLOW_PIP_INSTALL", "true").lower() != "true":
        return "[ERROR]: Package installation is disabled (set ALLOW_PIP_INSTALL=true to enable)."
    try:
        packages_dir = str(_packages_dir())
        result = subprocess.run(
            ["pip", "install", "--target", packages_dir, "--quiet", "--no-warn-script-location"]
            + package.split(),
            capture_output=True,
            text=True,
            timeout=TIMEOUT_INSTALL,
        )
        if result.returncode != 0:
            return f"[ERROR]: pip install failed:\n{result.stderr}"
        installed = [p.strip() for p in package.split() if p.strip()]
        return f"Installed: {', '.join(installed)} → {packages_dir}"
    except subprocess.TimeoutExpired:
        return "[ERROR]: pip install timed out (180s limit)."
    except Exception as e:
        return f"[ERROR]: {e}"


def pip_list() -> str:
    """
    List all Python packages currently installed in the persistent packages directory.
    Shows package name and version.
    """
    try:
        packages_dir = str(_packages_dir())
        result = subprocess.run(
            ["pip", "list", "--path", packages_dir, "--format=columns"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SHORT,
        )
        if result.returncode != 0:
            return f"[ERROR]: pip list failed:\n{result.stderr}"
        output = result.stdout.strip()
        if not output or output.startswith("Package") and len(output.splitlines()) <= 2:
            return "(no packages installed yet — use pip_install() to add packages)"
        lines = output.splitlines()
        return f"── Installed packages ({len(lines)-2} total) ──\n{output}"
    except Exception as e:
        return f"[ERROR]: {e}"


def python_env_info() -> str:
    """
    Show Python runtime information: version, executable path, workspace, and sys.path.
    Call this when you need to verify the environment before running code.
    """
    try:
        version_result = subprocess.run(
            ["python3", "--version"],
            capture_output=True, text=True
        )
        pip_version_result = subprocess.run(
            ["pip", "--version"],
            capture_output=True, text=True
        )

        workspace = str(_workspace())
        packages = str(_packages_dir())
        python_bin = sys.executable

        lines = [
            "── Python Environment ──",
            f"Python:       {version_result.stdout.strip() or version_result.stderr.strip()}",
            f"Executable:   {python_bin}",
            f"pip:          {pip_version_result.stdout.strip().split(' (')[0]}",
            f"Workspace:    {workspace}",
            f"Packages dir: {packages}",
        ]

        # Check if key tools are available
        tools_status = []
        for tool in ["ruff", "black", "pytest", "git"]:
            check = subprocess.run(
                ["which", tool], capture_output=True, text=True
            )
            status = "✓" if check.returncode == 0 else "✗ not installed"
            tools_status.append(f"  {tool:<10} {status}")

        lines.append("\nAvailable tools:")
        lines.extend(tools_status)

        return "\n".join(lines)
    except Exception as e:
        return f"[ERROR]: {e}"
