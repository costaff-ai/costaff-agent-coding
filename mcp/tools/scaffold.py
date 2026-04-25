"""
Scaffold tools — generate standard Python project structures and boilerplate.
"""
import re

from _shared import _safe_path, _workspace


_GITIGNORE = """\
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.env
.venv/
pip_packages/
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
"""

_PYPROJECT_TOML = """\
[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[tool.ruff]
line-length = 100

[tool.mypy]
strict = false
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
"""

_MAIN_PY = """\
def main():
    pass


if __name__ == "__main__":
    main()
"""

_TEST_PY = """\
from {name}.main import main


def test_placeholder():
    assert main() is None
"""


def scaffold_project(name: str, path: str = "") -> str:
    """
    Generate a standard Python project layout inside the workspace.
    Creates:
      src/{name}/__init__.py   — package init
      src/{name}/main.py       — entry point
      tests/__init__.py
      tests/test_main.py       — placeholder test
      pyproject.toml           — ruff / mypy / pytest config
      .gitignore
    name: Python package name — must be lowercase snake_case (e.g. 'my_app').
    path: subdirectory to scaffold into (default: workspace root).
    """
    if not re.match(r'^[a-z][a-z0-9_]*$', name):
        return "[ERROR]: name must be lowercase snake_case (e.g. 'my_app')."

    try:
        base = _safe_path(path) if path else _workspace()
        files = {
            f"src/{name}/__init__.py": f'"""{name} package."""\n',
            f"src/{name}/main.py":     _MAIN_PY,
            "tests/__init__.py":       "",
            f"tests/test_main.py":     _TEST_PY.format(name=name),
            "pyproject.toml":          _PYPROJECT_TOML.format(name=name),
            ".gitignore":              _GITIGNORE,
        }

        created, skipped = [], []
        for rel, content in files.items():
            target = base / rel
            if target.exists():
                skipped.append(rel)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            created.append(rel)

        lines = [f"── Scaffolded '{name}' ──"]
        if created:
            lines.append("Created:")
            lines += [f"  ✓ {f}" for f in created]
        if skipped:
            lines.append("Skipped (already exist):")
            lines += [f"  · {f}" for f in skipped]
        return "\n".join(lines)
    except ValueError as e:
        return f"[ERROR]: {e}"
    except Exception as e:
        return f"[ERROR]: {e}"
