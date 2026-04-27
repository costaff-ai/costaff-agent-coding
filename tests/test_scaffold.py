"""Tests for mcp/tools/scaffold.py"""
import pytest
from scaffold import scaffold_project


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_scaffold_creates_standard_layout(workspace):
    result = scaffold_project("my_app")
    assert "[ERROR]" not in result
    assert (workspace / "src" / "my_app" / "__init__.py").exists()
    assert (workspace / "src" / "my_app" / "main.py").exists()
    assert (workspace / "tests" / "__init__.py").exists()
    assert (workspace / "tests" / "test_main.py").exists()
    assert (workspace / "pyproject.toml").exists()
    assert (workspace / ".gitignore").exists()


def test_scaffold_pyproject_contains_name(workspace):
    scaffold_project("cool_pkg")
    content = (workspace / "pyproject.toml").read_text()
    assert 'name = "cool_pkg"' in content


def test_scaffold_test_file_imports_package(workspace):
    scaffold_project("my_lib")
    content = (workspace / "tests" / "test_main.py").read_text()
    assert "from my_lib.main import main" in content


def test_scaffold_in_subdirectory(workspace):
    (workspace / "projects").mkdir()
    result = scaffold_project("sub_app", "projects")
    assert "[ERROR]" not in result
    assert (workspace / "projects" / "src" / "sub_app" / "main.py").exists()


# ---------------------------------------------------------------------------
# Skips existing files
# ---------------------------------------------------------------------------

def test_scaffold_skips_existing_files(workspace):
    (workspace / "pyproject.toml").write_text("custom content")
    result = scaffold_project("my_app")
    assert "Skipped" in result
    assert (workspace / "pyproject.toml").read_text() == "custom content"


def test_scaffold_second_run_skips_all(workspace):
    scaffold_project("my_app")
    result = scaffold_project("my_app")
    assert "Created" not in result
    assert "Skipped" in result


# ---------------------------------------------------------------------------
# Invalid name validation
# ---------------------------------------------------------------------------

def test_scaffold_invalid_name_uppercase(workspace):
    result = scaffold_project("MyApp")
    assert "[ERROR]" in result


def test_scaffold_invalid_name_hyphen(workspace):
    result = scaffold_project("my-app")
    assert "[ERROR]" in result


def test_scaffold_invalid_name_starts_with_digit(workspace):
    result = scaffold_project("1app")
    assert "[ERROR]" in result


def test_scaffold_invalid_name_empty(workspace):
    result = scaffold_project("")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------

def test_scaffold_outside_workspace(workspace):
    result = scaffold_project("evil", "/tmp")
    assert "[ERROR]" in result
