---
name: git-workflow
description: "Perform git operations: stash, branch, merge, rebase, push, pull, commit, and manage history. Use for any version-control or source-management task."
---

# Git Workflow Skill

## Operations Reference

| Situation | Tool |
|-----------|------|
| Save uncommitted changes temporarily | `git_stash("push", message="wip: description")` |
| Restore stashed changes | `git_stash("pop")` |
| See all stashes | `git_stash("list")` |
| Create and switch to new branch | `git_checkout("feature/name", create=True)` |
| Switch to existing branch | `git_checkout("main")` |
| Merge a branch (preserving history) | `git_merge("feature/name", no_ff=True)` |
| Rebase onto upstream | `git_rebase("main")` |
| Stage and commit | `git_add(".")` → `git_commit("feat: message")` |
| Push to remote | `git_push()` |
| Pull latest | `git_pull()` |

## Standard Feature Branch Workflow
```
git_checkout("feature/my-feature", create=True)
# ... make changes ...
git_add("src/myfile.py tests/test_myfile.py")
git_commit("feat: add my feature")
git_checkout("main")
git_merge("feature/my-feature", no_ff=True)
```

## Merge vs Rebase
- **`git_merge` with `no_ff=True`**: preserves full branch history. Use when merging a feature branch into main.
- **`git_rebase`**: rewrites history for a clean linear log. Use to sync a feature branch with upstream main *before* merging.

## Authentication for Push / Pull
`git_push()` and `git_pull()` require `GIT_TOKEN` to be set. Check or set it:
```
dotenv_get("GIT_TOKEN")
dotenv_set("GIT_TOKEN", "<personal-access-token>")
```

## Commit Message Convention
```
feat: add new capability
fix: correct edge case in parser
refactor: extract helper function
test: add coverage for error path
docs: update README
```
