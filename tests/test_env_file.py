"""Tests for mcp/tools/env_file.py"""
import pytest
from env_file import dotenv_list, dotenv_get, dotenv_set, dotenv_delete


# ---------------------------------------------------------------------------
# dotenv_list
# ---------------------------------------------------------------------------

def test_dotenv_list_basic(workspace):
    (workspace / ".env").write_text("FOO=bar\nBAZ=123\n")
    result = dotenv_list(".env")
    assert "FOO=bar" in result
    assert "BAZ=123" in result


def test_dotenv_list_ignores_comments(workspace):
    (workspace / ".env").write_text("# comment\nKEY=val\n")
    result = dotenv_list(".env")
    assert "KEY=val" in result
    assert "comment" not in result


def test_dotenv_list_nonexistent(workspace):
    result = dotenv_list(".env")
    assert "does not exist" in result


def test_dotenv_list_empty_file(workspace):
    (workspace / ".env").write_text("")
    result = dotenv_list(".env")
    assert "empty" in result.lower()


def test_dotenv_list_strips_quotes(workspace):
    (workspace / ".env").write_text('KEY="quoted value"\n')
    result = dotenv_list(".env")
    assert "quoted value" in result


# ---------------------------------------------------------------------------
# dotenv_get
# ---------------------------------------------------------------------------

def test_dotenv_get_existing_key(workspace):
    (workspace / ".env").write_text("MY_KEY=my_value\n")
    result = dotenv_get("MY_KEY", ".env")
    assert result == "my_value"


def test_dotenv_get_missing_key(workspace):
    (workspace / ".env").write_text("OTHER=x\n")
    result = dotenv_get("MISSING", ".env")
    assert "[ERROR]" in result


def test_dotenv_get_nonexistent_file(workspace):
    result = dotenv_get("KEY", ".env")
    assert "[ERROR]" in result


def test_dotenv_get_quoted_value(workspace):
    (workspace / ".env").write_text("TOKEN='secret'\n")
    result = dotenv_get("TOKEN", ".env")
    assert result == "secret"


# ---------------------------------------------------------------------------
# dotenv_set
# ---------------------------------------------------------------------------

def test_dotenv_set_new_key(workspace):
    (workspace / ".env").write_text("")
    result = dotenv_set("NEW_KEY", "new_val", ".env")
    assert "[ERROR]" not in result
    assert "Added" in result
    assert "NEW_KEY=new_val" in (workspace / ".env").read_text()


def test_dotenv_set_updates_existing(workspace):
    (workspace / ".env").write_text("KEY=old\n")
    result = dotenv_set("KEY", "new", ".env")
    assert "Updated" in result
    content = (workspace / ".env").read_text()
    assert "KEY=new" in content
    assert "KEY=old" not in content


def test_dotenv_set_creates_file(workspace):
    result = dotenv_set("BRAND_NEW", "value", ".env")
    assert "[ERROR]" not in result
    assert (workspace / ".env").exists()


def test_dotenv_set_invalid_key_name(workspace):
    result = dotenv_set("123INVALID", "val", ".env")
    assert "[ERROR]" in result


def test_dotenv_set_key_with_spaces_invalid(workspace):
    result = dotenv_set("KEY WITH SPACES", "val", ".env")
    assert "[ERROR]" in result


def test_dotenv_set_outside_workspace(workspace):
    result = dotenv_set("KEY", "val", "/etc/.env")
    assert "[ERROR]" in result


# ---------------------------------------------------------------------------
# dotenv_delete
# ---------------------------------------------------------------------------

def test_dotenv_delete_existing_key(workspace):
    (workspace / ".env").write_text("KEEP=yes\nDEL=this\n")
    result = dotenv_delete("DEL", ".env")
    assert "[ERROR]" not in result
    content = (workspace / ".env").read_text()
    assert "DEL" not in content
    assert "KEEP=yes" in content


def test_dotenv_delete_missing_key(workspace):
    (workspace / ".env").write_text("KEY=val\n")
    result = dotenv_delete("NOTHERE", ".env")
    assert "[ERROR]" in result


def test_dotenv_delete_nonexistent_file(workspace):
    result = dotenv_delete("KEY", ".env")
    assert "[ERROR]" in result


def test_dotenv_delete_preserves_other_keys(workspace):
    (workspace / ".env").write_text("A=1\nB=2\nC=3\n")
    dotenv_delete("B", ".env")
    content = (workspace / ".env").read_text()
    assert "A=1" in content
    assert "C=3" in content
    assert "B" not in content
