"""Tests for mcp/tools/reading.py"""
import json
import pytest
from reading import (
    read_file, read_lines, head, tail,
    outline, grep, find_files, query_json, diff_files,
)


# ---------------------------------------------------------------------------
# read_file
# ---------------------------------------------------------------------------

def test_read_file_basic(workspace):
    (workspace / "hello.txt").write_text("line1\nline2\nline3\n")
    result = read_file("hello.txt")
    assert "line1" in result
    assert "line2" in result
    assert "3 lines" in result or "   1" in result


def test_read_file_nonexistent(workspace):
    result = read_file("nope.txt")
    assert "[ERROR]" in result


def test_read_file_on_directory(workspace):
    (workspace / "d").mkdir()
    result = read_file("d")
    assert "[ERROR]" in result


def test_read_file_outside_workspace(workspace):
    result = read_file("/etc/hosts")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# read_lines
# ---------------------------------------------------------------------------

def test_read_lines_middle(workspace):
    (workspace / "f.txt").write_text("\n".join(str(i) for i in range(1, 11)))
    result = read_lines("f.txt", 3, 5)
    assert "3" in result
    assert "5" in result
    assert "1\n" not in result


def test_read_lines_clamps_to_file_length(workspace):
    (workspace / "f.txt").write_text("a\nb\nc\n")
    result = read_lines("f.txt", 1, 100)
    assert "[ERROR]" not in result
    assert "a" in result


def test_read_lines_start_beyond_eof(workspace):
    (workspace / "f.txt").write_text("a\nb\n")
    result = read_lines("f.txt", 99, 100)
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# head / tail
# ---------------------------------------------------------------------------

def test_head_default(workspace):
    lines = [f"line{i}" for i in range(50)]
    (workspace / "big.txt").write_text("\n".join(lines))
    result = head("big.txt")
    assert "line0" in result
    assert "line29" in result
    assert "line30" not in result


def test_head_custom_n(workspace):
    (workspace / "f.txt").write_text("a\nb\nc\nd\ne\n")
    result = head("f.txt", n=2)
    assert "a" in result
    assert "c" not in result


def test_tail_default(workspace):
    lines = [f"line{i}" for i in range(50)]
    (workspace / "big.txt").write_text("\n".join(lines))
    result = tail("big.txt")
    assert "line49" in result
    assert "line0" not in result


def test_tail_custom_n(workspace):
    (workspace / "f.txt").write_text("a\nb\nc\nd\ne\n")
    result = tail("f.txt", n=2)
    assert "│ e" in result
    assert "│ a" not in result


def test_head_nonexistent(workspace):
    assert "[ERROR]" in head("ghost.txt")


def test_tail_nonexistent(workspace):
    assert "[ERROR]" in tail("ghost.txt")


# ---------------------------------------------------------------------------
# outline
# ---------------------------------------------------------------------------

def test_outline_classes_and_functions(workspace):
    code = """\
class Foo:
    def bar(self):
        pass

def top_level():
    pass
"""
    (workspace / "mod.py").write_text(code)
    result = outline("mod.py")
    assert "class Foo:" in result
    assert "def bar()" in result
    assert "def top_level()" in result


def test_outline_non_py_file(workspace):
    (workspace / "readme.md").write_text("# hi")
    result = outline("readme.md")
    assert "[ERROR]" in result


def test_outline_syntax_error(workspace):
    (workspace / "bad.py").write_text("def broken(:\n    pass\n")
    result = outline("bad.py")
    assert "[ERROR]" in result


def test_outline_empty_file(workspace):
    (workspace / "empty.py").write_text("")
    result = outline("empty.py")
    assert "no classes or functions" in result


# ---------------------------------------------------------------------------
# grep
# ---------------------------------------------------------------------------

def test_grep_finds_match(workspace):
    (workspace / "a.py").write_text("foo = 1\nbar = 2\n")
    # context=0 so only matched line is shown
    result = grep("foo", "a.py", context=0)
    assert "► L" in result   # match marker present
    assert "foo = 1" in result
    assert "bar" not in result  # context=0, adjacent line excluded


def test_grep_no_match(workspace):
    (workspace / "a.py").write_text("nothing here\n")
    result = grep("xyz_notfound", "a.py")
    assert "No matches" in result


def test_grep_recursive(workspace):
    (workspace / "sub").mkdir()
    (workspace / "sub" / "b.py").write_text("target_string\n")
    result = grep("target_string", "")
    assert "target_string" in result
    assert "b.py" in result


def test_grep_invalid_regex(workspace):
    result = grep("[invalid", "")
    assert "[ERROR]" in result


def test_grep_nonexistent_path(workspace):
    result = grep("x", "does_not_exist")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# find_files
# ---------------------------------------------------------------------------

def test_find_files_by_extension(workspace):
    (workspace / "a.py").write_text("")
    (workspace / "b.txt").write_text("")
    result = find_files("**/*.py")
    assert "a.py" in result
    assert "b.txt" not in result


def test_find_files_no_match(workspace):
    result = find_files("**/*.xyz")
    assert "No files found" in result


def test_find_files_in_subdir(workspace):
    (workspace / "src").mkdir()
    (workspace / "src" / "main.py").write_text("")
    result = find_files("**/*.py", "src")
    assert "main.py" in result


# ---------------------------------------------------------------------------
# query_json
# ---------------------------------------------------------------------------

def test_query_json_full(workspace):
    data = {"key": "value", "num": 42}
    (workspace / "data.json").write_text(json.dumps(data))
    result = query_json("data.json")
    assert '"key"' in result
    assert '"value"' in result


def test_query_json_expression(workspace):
    data = {"server": {"host": "localhost", "port": 8080}}
    (workspace / "cfg.json").write_text(json.dumps(data))
    result = query_json("cfg.json", "server.host")
    assert "localhost" in result


def test_query_json_list_index(workspace):
    (workspace / "list.json").write_text(json.dumps([10, 20, 30]))
    result = query_json("list.json", "1")
    assert "20" in result


def test_query_json_missing_key(workspace):
    (workspace / "d.json").write_text('{"a": 1}')
    result = query_json("d.json", "missing_key")
    assert "[ERROR]" in result


def test_query_json_invalid_json(workspace):
    (workspace / "bad.json").write_text("{not valid}")
    result = query_json("bad.json")
    assert "[ERROR]" in result


def test_query_json_nonexistent(workspace):
    result = query_json("ghost.json")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# diff_files
# ---------------------------------------------------------------------------

def test_diff_files_identical(workspace):
    (workspace / "a.txt").write_text("same content\n")
    (workspace / "b.txt").write_text("same content\n")
    result = diff_files("a.txt", "b.txt")
    assert "identical" in result


def test_diff_files_different(workspace):
    (workspace / "a.txt").write_text("line1\nline2\n")
    (workspace / "b.txt").write_text("line1\nline3\n")
    result = diff_files("a.txt", "b.txt")
    assert "line2" in result or "line3" in result


def test_diff_files_missing_a(workspace):
    (workspace / "b.txt").write_text("x")
    result = diff_files("ghost.txt", "b.txt")
    assert "[ERROR]" in result


def test_diff_files_missing_b(workspace):
    (workspace / "a.txt").write_text("x")
    result = diff_files("a.txt", "ghost.txt")
    assert "[ERROR]" in result
