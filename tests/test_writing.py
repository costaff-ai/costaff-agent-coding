"""Tests for mcp/tools/writing.py"""
import pytest
from writing import write_file, append_file, patch_file, insert_after_line


# ---------------------------------------------------------------------------
# write_file
# ---------------------------------------------------------------------------

def test_write_file_creates_new(workspace):
    result = write_file("new.txt", "hello world")
    assert "[ERROR]" not in result
    assert (workspace / "new.txt").read_text() == "hello world"


def test_write_file_overwrites_existing(workspace):
    (workspace / "f.txt").write_text("old content")
    write_file("f.txt", "new content")
    assert (workspace / "f.txt").read_text() == "new content"


def test_write_file_creates_parent_dirs(workspace):
    result = write_file("a/b/c.txt", "deep")
    assert "[ERROR]" not in result
    assert (workspace / "a" / "b" / "c.txt").exists()


def test_write_file_outside_workspace(workspace):
    result = write_file("/etc/evil.txt", "bad")
    assert "[ERROR]" in result


def test_write_file_reports_line_count(workspace):
    result = write_file("multi.txt", "a\nb\nc")
    assert "3" in result or "lines" in result


# ---------------------------------------------------------------------------
# append_file
# ---------------------------------------------------------------------------

def test_append_file_basic(workspace):
    (workspace / "f.txt").write_text("first\n")
    result = append_file("f.txt", "second\n")
    assert "[ERROR]" not in result
    content = (workspace / "f.txt").read_text()
    assert content == "first\nsecond\n"


def test_append_file_adds_newline_separator(workspace):
    (workspace / "f.txt").write_text("no newline at end")
    append_file("f.txt", "appended")
    content = (workspace / "f.txt").read_text()
    assert "no newline at end\nappended" in content


def test_append_file_nonexistent(workspace):
    result = append_file("ghost.txt", "data")
    assert "[ERROR]" in result


def test_append_file_outside_workspace(workspace):
    result = append_file("/etc/hosts", "evil")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# patch_file
# ---------------------------------------------------------------------------

def test_patch_file_basic(workspace):
    (workspace / "f.py").write_text("def foo():\n    return 1\n")
    result = patch_file("f.py", "return 1", "return 42")
    assert "[ERROR]" not in result
    assert (workspace / "f.py").read_text() == "def foo():\n    return 42\n"


def test_patch_file_old_str_not_found(workspace):
    (workspace / "f.py").write_text("def foo(): pass\n")
    result = patch_file("f.py", "does_not_exist", "new")
    assert "[ERROR]" in result


def test_patch_file_multiple_matches(workspace):
    (workspace / "f.py").write_text("x = 1\nx = 1\n")
    result = patch_file("f.py", "x = 1", "x = 2")
    assert "[ERROR]" in result
    assert "2 location" in result


def test_patch_file_delete_block(workspace):
    (workspace / "f.py").write_text("keep\ndelete_me\nkeep\n")
    patch_file("f.py", "delete_me\n", "")
    content = (workspace / "f.py").read_text()
    assert "delete_me" not in content
    assert "keep" in content


def test_patch_file_nonexistent(workspace):
    result = patch_file("ghost.py", "x", "y")
    assert "[ERROR]" in result


def test_patch_file_outside_workspace(workspace):
    result = patch_file("/etc/hosts", "localhost", "evil")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# insert_after_line
# ---------------------------------------------------------------------------

def test_insert_after_line_middle(workspace):
    (workspace / "f.txt").write_text("line1\nline2\nline3\n")
    result = insert_after_line("f.txt", 1, "inserted\n")
    assert "[ERROR]" not in result
    lines = (workspace / "f.txt").read_text().splitlines()
    assert lines[0] == "line1"
    assert lines[1] == "inserted"
    assert lines[2] == "line2"


def test_insert_after_line_zero_inserts_at_top(workspace):
    (workspace / "f.txt").write_text("existing\n")
    insert_after_line("f.txt", 0, "prepended")
    lines = (workspace / "f.txt").read_text().splitlines()
    assert lines[0] == "prepended"
    assert lines[1] == "existing"


def test_insert_after_line_at_end(workspace):
    (workspace / "f.txt").write_text("a\nb\n")
    result = insert_after_line("f.txt", 2, "c")
    assert "[ERROR]" not in result
    assert "c" in (workspace / "f.txt").read_text()


def test_insert_after_line_out_of_range(workspace):
    (workspace / "f.txt").write_text("a\nb\n")
    result = insert_after_line("f.txt", 99, "x")
    assert "[ERROR]" in result


def test_insert_after_line_nonexistent(workspace):
    result = insert_after_line("ghost.txt", 1, "x")
    assert "[ERROR]" in result
