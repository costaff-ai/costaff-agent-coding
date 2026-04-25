"""
Git tools — version control operations within the workspace.

Safe operations (always available):
  git_init, git_status, git_add, git_commit, git_log, git_diff,
  git_branch, git_checkout, git_clone

Authenticated operations (require GIT_TOKEN env var):
  git_push, git_pull

Branch management (always available):
  git_stash, git_merge, git_rebase

Credential setup (env vars read at call time):
  GIT_TOKEN        — Personal Access Token for HTTPS push/pull
  GIT_AUTHOR_NAME  — Commit author name  (default: "Coding Agent")
  GIT_AUTHOR_EMAIL — Commit author email (default: "agent@costaff.ai")
"""
import os
import re
import subprocess
from pathlib import Path

from _shared import _safe_path, _workspace, TIMEOUT_MEDIUM

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run_git(args: list[str], cwd: Path, env: dict | None = None) -> str:
    """Run a git command and return combined stdout+stderr."""
    base_env = os.environ.copy()
    if env:
        base_env.update(env)
    # Disable interactive prompts — fail fast instead of hanging
    base_env["GIT_TERMINAL_PROMPT"] = "0"

    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_MEDIUM,
            cwd=str(cwd),
            env=base_env,
        )
        output = result.stdout.strip()
        if result.stderr.strip():
            output = (output + "\n[STDERR]:\n" + result.stderr.strip()).strip()
        if result.returncode != 0 and not output:
            output = f"[EXIT CODE]: {result.returncode}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "[ERROR]: git command timed out (60s limit)."
    except FileNotFoundError:
        return "[ERROR]: git is not installed in this container."
    except Exception as e:
        return f"[ERROR]: {e}"


def _repo_path(path: str) -> Path:
    """Resolve a workspace-relative path for git operations."""
    if path:
        return _safe_path(path)
    return _workspace()


def _inject_token(url: str, token: str) -> str:
    """
    Inject a PAT token into an HTTPS GitHub/GitLab URL.
    https://github.com/org/repo  →  https://<token>@github.com/org/repo
    """
    return re.sub(r"^(https?://)", rf"\1{token}@", url)


def _author_env() -> dict:
    return {
        "GIT_AUTHOR_NAME":    os.getenv("GIT_AUTHOR_NAME",  "Coding Agent"),
        "GIT_AUTHOR_EMAIL":   os.getenv("GIT_AUTHOR_EMAIL", "agent@costaff.ai"),
        "GIT_COMMITTER_NAME": os.getenv("GIT_AUTHOR_NAME",  "Coding Agent"),
        "GIT_COMMITTER_EMAIL":os.getenv("GIT_AUTHOR_EMAIL", "agent@costaff.ai"),
    }


def _run_git_authed(args: list[str], remote: str, repo: Path, token: str) -> str:
    """Run a git command with HTTPS token auth, restoring the original remote URL after."""
    get_url = _run_git(["remote", "get-url", remote], cwd=repo)
    is_https = get_url.startswith("http")
    if is_https:
        _run_git(["remote", "set-url", remote, _inject_token(get_url.strip(), token)], cwd=repo)
    try:
        return _run_git(args, cwd=repo)
    finally:
        if is_https:
            _run_git(["remote", "set-url", remote, get_url.strip()], cwd=repo)


# ---------------------------------------------------------------------------
# Public tools (auto-registered by server.py)
# ---------------------------------------------------------------------------

def git_init(path: str = "") -> str:
    """
    Initialise a new git repository in the workspace (or a sub-directory).
    path: relative path within workspace to initialise (default: workspace root).
    """
    try:
        target = _repo_path(path)
        target.mkdir(parents=True, exist_ok=True)
        return _run_git(["init"], cwd=target)
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_status(path: str = "") -> str:
    """
    Show the working-tree status of a repository.
    path: relative path to the repository root within workspace (default: workspace root).
    """
    try:
        return _run_git(["status", "--short", "--branch"], cwd=_repo_path(path))
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_add(files: str = ".", path: str = "") -> str:
    """
    Stage files for the next commit.
    files: space-separated list of files/patterns to stage (default: '.' stages everything).
    path:  relative path to the repository root within workspace (default: workspace root).
    """
    try:
        file_list = files.split() if files != "." else ["."]
        return _run_git(["add"] + file_list, cwd=_repo_path(path))
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_commit(message: str, path: str = "") -> str:
    """
    Commit staged changes.
    message: commit message (required).
    path:    relative path to the repository root within workspace (default: workspace root).
    """
    if not message or not message.strip():
        return "[ERROR]: Commit message cannot be empty."
    try:
        return _run_git(
            ["commit", "-m", message],
            cwd=_repo_path(path),
            env=_author_env(),
        )
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_log(path: str = "", limit: int = 10) -> str:
    """
    Show recent commit history.
    path:  relative path to the repository root within workspace (default: workspace root).
    limit: maximum number of commits to show (default: 10).
    """
    try:
        limit = max(1, min(limit, 100))
        return _run_git(
            ["log", f"--max-count={limit}", "--oneline", "--decorate"],
            cwd=_repo_path(path),
        )
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_diff(path: str = "", staged: bool = False) -> str:
    """
    Show unstaged (or staged) changes.
    path:   relative path to the repository root within workspace (default: workspace root).
    staged: if True, show staged diff (git diff --cached); otherwise show working-tree diff.
    """
    try:
        args = ["diff"]
        if staged:
            args.append("--cached")
        args += ["--stat", "--patch"]
        return _run_git(args, cwd=_repo_path(path))
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_branch(path: str = "") -> str:
    """
    List all local branches and highlight the current one.
    path: relative path to the repository root within workspace (default: workspace root).
    """
    try:
        return _run_git(["branch", "-v"], cwd=_repo_path(path))
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_checkout(branch: str, path: str = "", create: bool = False) -> str:
    """
    Switch to an existing branch or create a new one.
    branch: branch name to switch to or create.
    path:   relative path to the repository root within workspace (default: workspace root).
    create: if True, create the branch first (git checkout -b).
    """
    if not branch or not branch.strip():
        return "[ERROR]: Branch name cannot be empty."
    try:
        args = ["checkout", "-b", branch] if create else ["checkout", branch]
        return _run_git(args, cwd=_repo_path(path))
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_clone(url: str, dest: str = "") -> str:
    """
    Clone a remote repository into the workspace.
    url:  HTTPS or SSH URL of the repository to clone.
    dest: destination folder name within the workspace (default: repo name from URL).

    For private repos over HTTPS, set the GIT_TOKEN environment variable.
    SSH clones work only if an SSH key is mounted at /root/.ssh/.
    """
    if not url or not url.strip():
        return "[ERROR]: URL cannot be empty."

    token = os.getenv("GIT_TOKEN", "")
    clone_url = _inject_token(url, token) if token and url.startswith("http") else url

    try:
        workspace = _workspace()
        args = ["clone", clone_url]
        if dest:
            # Validate dest is workspace-relative
            target = _safe_path(dest)
            args.append(str(target))
        return _run_git(args, cwd=workspace)
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_push(remote: str = "origin", branch: str = "", path: str = "") -> str:
    """
    Push commits to a remote repository.
    Requires the GIT_TOKEN environment variable to be set for HTTPS remotes.

    remote: remote name (default: 'origin').
    branch: branch to push (default: current branch).
    path:   relative path to the repository root within workspace (default: workspace root).
    """
    token = os.getenv("GIT_TOKEN", "")
    if not token:
        return (
            "[ERROR]: GIT_TOKEN is not set. "
            "Add GIT_TOKEN=<your-personal-access-token> to your .env file to enable push."
        )
    try:
        repo = _repo_path(path)
        args = ["push", remote] + ([branch] if branch else [])
        return _run_git_authed(args, remote, repo, token)
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_pull(remote: str = "origin", branch: str = "", path: str = "") -> str:
    """
    Pull latest changes from a remote repository.
    Requires the GIT_TOKEN environment variable to be set for HTTPS remotes.

    remote: remote name (default: 'origin').
    branch: branch to pull (default: current tracking branch).
    path:   relative path to the repository root within workspace (default: workspace root).
    """
    token = os.getenv("GIT_TOKEN", "")
    if not token:
        return (
            "[ERROR]: GIT_TOKEN is not set. "
            "Add GIT_TOKEN=<your-personal-access-token> to your .env file to enable pull."
        )
    try:
        repo = _repo_path(path)
        args = ["pull", remote] + ([branch] if branch else [])
        return _run_git_authed(args, remote, repo, token)
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_stash(action: str = "push", message: str = "", path: str = "") -> str:
    """
    Manage the git stash.
    action: 'push' (save changes, default), 'pop' (restore latest), 'list', or 'drop'.
    message: optional description label (only applies to push).
    path: relative path to the repository root within workspace.
    """
    valid = {"push", "pop", "list", "drop"}
    if action not in valid:
        return f"[ERROR]: action must be one of: {', '.join(sorted(valid))}."
    try:
        if action == "push":
            args = ["stash", "push"] + (["-m", message] if message else [])
        else:
            args = ["stash", action]
        return _run_git(args, cwd=_repo_path(path))
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_merge(branch: str, path: str = "", no_ff: bool = False) -> str:
    """
    Merge a branch into the current branch.
    branch: the branch name to merge from.
    path: relative path to the repository root within workspace.
    no_ff: always create a merge commit, even for fast-forwards (--no-ff).
    """
    if not branch or not branch.strip():
        return "[ERROR]: Branch name cannot be empty."
    try:
        args = ["merge", branch] + (["--no-ff"] if no_ff else [])
        return _run_git(args, cwd=_repo_path(path), env=_author_env())
    except ValueError as e:
        return f"[ERROR]: {e}"


def git_rebase(base: str, path: str = "") -> str:
    """
    Rebase the current branch onto another branch or commit.
    base: the branch name or commit SHA to rebase onto.
    path: relative path to the repository root within workspace.
    """
    if not base or not base.strip():
        return "[ERROR]: Base branch/commit cannot be empty."
    try:
        return _run_git(["rebase", base], cwd=_repo_path(path), env=_author_env())
    except ValueError as e:
        return f"[ERROR]: {e}"
