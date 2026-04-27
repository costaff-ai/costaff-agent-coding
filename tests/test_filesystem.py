"""Tests for mcp/tools/filesystem.py"""
import os
import pytest
from filesystem import ls, tree, mkdir, mv, cp, rm, file_info


# ---------------------------------------------------------------------------
# ls
# ---------------------------------------------------------------------------

def test_ls_empty_workspace(workspace):
    result = ls("")
    # empty workspace returns "(empty directory)" with no header
    assert "empty" in result.lower()


def test_ls_shows_files_and_dirs(workspace):
    (workspace / "file.txt").write_text("hello")
    (workspace / "subdir").mkdir()
    result = ls("")
    assert "file.txt" in result
    assert "subdir" in result
    assert "FILE" in result
    assert "DIR" in result


def test_ls_nonexistent_path(workspace):
    result = ls("does_not_exist")
    assert "[ERROR]" in result


def test_ls_file_instead_of_dir(workspace):
    (workspace / "f.txt").write_text("x")
    result = ls("f.txt")
    assert "[ERROR]" in result


def test_ls_outside_workspace(workspace):
    result = ls("/etc")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# tree
# ---------------------------------------------------------------------------

def test_tree_empty(workspace):
    result = tree("")
    assert "workspace/" in result


def test_tree_nested(workspace):
    (workspace / "a" / "b").mkdir(parents=True)
    (workspace / "a" / "b" / "c.py").write_text("")
    result = tree("")
    assert "a" in result
    assert "b" in result
    assert "c.py" in result


def test_tree_depth_limit(workspace):
    (workspace / "a" / "b" / "c" / "d").mkdir(parents=True)
    result = tree("", depth=2)
    assert "a" in result
    assert "b" in result
    assert "d" not in result


def test_tree_nonexistent(workspace):
    result = tree("ghost")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# mkdir
# ---------------------------------------------------------------------------

def test_mkdir_creates_directory(workspace):
    result = mkdir("new_dir")
    assert "[ERROR]" not in result
    assert (workspace / "new_dir").is_dir()


def test_mkdir_creates_nested(workspace):
    result = mkdir("a/b/c")
    assert "[ERROR]" not in result
    assert (workspace / "a" / "b" / "c").is_dir()


def test_mkdir_already_exists(workspace):
    (workspace / "existing").mkdir()
    result = mkdir("existing")
    assert "[ERROR]" not in result  # exist_ok=True, no error


def test_mkdir_outside_workspace(workspace):
    result = mkdir("/etc/evil")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# mv
# ---------------------------------------------------------------------------

def test_mv_file(workspace):
    (workspace / "src.txt").write_text("data")
    result = mv("src.txt", "dst.txt")
    assert "[ERROR]" not in result
    assert not (workspace / "src.txt").exists()
    assert (workspace / "dst.txt").read_text() == "data"


def test_mv_nonexistent_source(workspace):
    result = mv("ghost.txt", "dst.txt")
    assert "[ERROR]" in result


def test_mv_creates_parent_dirs(workspace):
    (workspace / "f.txt").write_text("x")
    result = mv("f.txt", "sub/dir/f.txt")
    assert "[ERROR]" not in result
    assert (workspace / "sub" / "dir" / "f.txt").exists()


def test_mv_outside_workspace(workspace):
    (workspace / "f.txt").write_text("x")
    result = mv("f.txt", "/tmp/evil.txt")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# cp
# ---------------------------------------------------------------------------

def test_cp_file(workspace):
    (workspace / "orig.txt").write_text("content")
    result = cp("orig.txt", "copy.txt")
    assert "[ERROR]" not in result
    assert (workspace / "orig.txt").exists()
    assert (workspace / "copy.txt").read_text() == "content"


def test_cp_directory(workspace):
    (workspace / "src_dir").mkdir()
    (workspace / "src_dir" / "a.txt").write_text("a")
    result = cp("src_dir", "dst_dir")
    assert "[ERROR]" not in result
    assert (workspace / "dst_dir" / "a.txt").read_text() == "a"


def test_cp_nonexistent_source(workspace):
    result = cp("ghost.txt", "dst.txt")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# rm
# ---------------------------------------------------------------------------

def test_rm_file(workspace):
    (workspace / "del.txt").write_text("bye")
    result = rm("del.txt")
    assert "[ERROR]" not in result
    assert not (workspace / "del.txt").exists()


def test_rm_empty_dir(workspace):
    (workspace / "empty_dir").mkdir()
    result = rm("empty_dir")
    assert "[ERROR]" not in result
    assert not (workspace / "empty_dir").exists()


def test_rm_nonempty_dir_without_recursive(workspace):
    d = workspace / "full_dir"
    d.mkdir()
    (d / "file.txt").write_text("x")
    result = rm("full_dir")
    assert "[ERROR]" in result
    assert d.exists()


def test_rm_nonempty_dir_with_recursive(workspace):
    d = workspace / "full_dir"
    d.mkdir()
    (d / "file.txt").write_text("x")
    result = rm("full_dir", recursive=True)
    assert "[ERROR]" not in result
    assert not d.exists()


def test_rm_nonexistent(workspace):
    result = rm("ghost.txt")
    assert "[ERROR]" in result


def test_rm_outside_workspace(workspace):
    result = rm("/etc/passwd")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# file_info
# ---------------------------------------------------------------------------

def test_file_info_file(workspace):
    (workspace / "info.txt").write_text("line1\nline2\n")
    result = file_info("info.txt")
    assert "Lines" in result
    assert "Size" in result
    assert "[ERROR]" not in result


def test_file_info_directory(workspace):
    (workspace / "d").mkdir()
    (workspace / "d" / "a.py").write_text("x")
    result = file_info("d")
    assert "directory" in result
    assert "[ERROR]" not in result


def test_file_info_nonexistent(workspace):
    result = file_info("ghost.txt")
    assert "[ERROR]" in result
