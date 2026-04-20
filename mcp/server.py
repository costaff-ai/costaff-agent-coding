import os
import subprocess
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-coding")

WORKSPACE = os.getenv("CODING_WORKSPACE_DIR", "/app/data/coding_workspace")
PACKAGES_DIR = os.path.join(os.path.dirname(WORKSPACE), "pip_packages")
ALLOW_PIP_INSTALL = os.getenv("ALLOW_PIP_INSTALL", "true").lower() not in ("false", "0", "no")
os.makedirs(WORKSPACE, exist_ok=True)
os.makedirs(PACKAGES_DIR, exist_ok=True)

mcp = FastMCP("Coding", host="0.0.0.0", port=int(os.getenv("MCP_CODING_PORT", "8082")))


@mcp.tool()
def install_package(package: str) -> str:
    """
    Install a Python package using pip. Packages are installed to a persistent
    directory and survive container restarts.
    Only available when ALLOW_PIP_INSTALL is enabled (default: true).
    """
    if not ALLOW_PIP_INSTALL:
        return "[ERROR]: Package installation is disabled (ALLOW_PIP_INSTALL=false)."
    try:
        result = subprocess.run(
            ["pip", "install", "--target", PACKAGES_DIR, "--quiet", package],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return f"[ERROR]: pip install failed:\n{result.stderr}"
        return f"Package '{package}' installed successfully to {PACKAGES_DIR}."
    except subprocess.TimeoutExpired:
        return "[ERROR]: pip install timed out (120s limit)."
    except Exception as e:
        return f"[ERROR]: {e}"


@mcp.tool()
def execute_python(code: str) -> str:
    """
    Execute Python code and return the output.
    Use this to run computations, data processing, or any logic that requires code execution.
    The code runs in an isolated workspace directory.
    """
    try:
        inject = (
            f"import sys; sys.path.insert(0, {PACKAGES_DIR!r})\n"
            "try:\n"
            "    import matplotlib, matplotlib.font_manager as _fm\n"
            "    _fp = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'\n"
            "    if __import__('os').path.exists(_fp): _fm.fontManager.addfont(_fp)\n"
            "    _prop = _fm.FontProperties(fname=_fp) if __import__('os').path.exists(_fp) else None\n"
            "    if _prop: matplotlib.rcParams['font.family'] = _prop.get_name()\n"
            "    matplotlib.rcParams['axes.unicode_minus'] = False\n"
            "except Exception: pass\n"
        )
        result = subprocess.run(
            ["python3", "-c", inject + code],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=WORKSPACE,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]:\n{result.stderr}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "[ERROR]: Code execution timed out (60s limit)."
    except Exception as e:
        return f"[ERROR]: {e}"


@mcp.tool()
def execute_python_file(filename: str) -> str:
    """
    Execute a Python file that exists in the coding workspace.
    Use this after writing a script with write_file().
    """
    filepath = Path(WORKSPACE) / filename
    if not filepath.exists():
        return f"[ERROR]: File '{filename}' not found in workspace."
    try:
        result = subprocess.run(
            ["python3", "-c", (
                f"import sys; sys.path.insert(0, {PACKAGES_DIR!r})\n"
                "try:\n"
                "    import matplotlib, matplotlib.font_manager as _fm\n"
                "    _cjk = [f.name for f in _fm.fontManager.ttflist if 'Noto' in f.name and 'CJK' in f.name]\n"
                "    if _cjk: matplotlib.rcParams['font.family'] = _cjk[0]\n"
                "    matplotlib.rcParams['axes.unicode_minus'] = False\n"
                "except Exception: pass\n"
                f"exec(open({str(filepath)!r}).read())"
            )],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=WORKSPACE,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]:\n{result.stderr}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "[ERROR]: Execution timed out (120s limit)."
    except Exception as e:
        return f"[ERROR]: {e}"


@mcp.tool()
def write_file(filename: str, content: str) -> str:
    """
    Write content to a file in the coding workspace.
    Use this to save scripts, data files, or generated output.
    """
    try:
        filepath = Path(WORKSPACE) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")
        return f"File '{filename}' written successfully ({len(content)} chars)."
    except Exception as e:
        return f"[ERROR]: {e}"


@mcp.tool()
def read_file(filename: str) -> str:
    """
    Read the content of a file from the coding workspace.
    """
    try:
        filepath = Path(WORKSPACE) / filename
        if not filepath.exists():
            return f"[ERROR]: File '{filename}' not found."
        return filepath.read_text(encoding="utf-8")
    except Exception as e:
        return f"[ERROR]: {e}"


@mcp.tool()
def list_workspace() -> str:
    """
    List all files currently in the coding workspace.
    """
    try:
        files = sorted(Path(WORKSPACE).rglob("*"))
        if not files:
            return "(workspace is empty)"
        return "\n".join(
            str(f.relative_to(WORKSPACE)) + ("/" if f.is_dir() else "")
            for f in files
        )
    except Exception as e:
        return f"[ERROR]: {e}"


@mcp.tool()
def delete_file(filename: str) -> str:
    """
    Delete a file from the coding workspace.
    """
    try:
        filepath = Path(WORKSPACE) / filename
        if not filepath.exists():
            return f"[ERROR]: File '{filename}' not found."
        filepath.unlink()
        return f"File '{filename}' deleted."
    except Exception as e:
        return f"[ERROR]: {e}"


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "sse")
    logger.info(f"Starting Coding MCP server (transport={transport}, workspace={WORKSPACE})")
    mcp.run(transport=transport)
