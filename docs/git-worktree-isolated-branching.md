# Isolated Branching With Worktrees

Use this when the current checkout has unrelated local changes, or when multiple
agents are working in parallel and one change needs its own clean branch or PR.

## Worktree Location

Prefer a sibling `worktrees/` directory when the repository lives inside a
workspace that keeps related checkouts together. From this repository directory,
that is usually:

```text
../worktrees
```

System temporary directories are fine for short-lived patch files or disposable
scratch, but durable worktrees should live in the sibling `worktrees/` directory.
Do not move or delete existing worktrees unless explicitly asked.

## Flow

1. Pick a short slug and branch prefix.

Use the repository branch convention from `AGENTS.md`; for this repo, use
`jab/<short-slug>`.

2. If isolating existing local changes, capture only the intended diff.

```bash
git diff -- path/to/file > /tmp/<short-slug>.patch
```

Skip this step when starting fresh.

3. Refresh the base branch.

```bash
git fetch origin main
```

4. Create the worktree.

```bash
git worktree add -b <prefix>/<short-slug> \
  ../worktrees/<repo>-<short-slug> \
  FETCH_HEAD
```

5. Apply the patch if one was captured.

```bash
cd ../worktrees/<repo>-<short-slug>
git apply /tmp/<short-slug>.patch
```

6. Bring over ignored local state only when needed.

Git worktrees contain tracked files only. Copy or symlink only the local env,
cache, or data files needed for validation, and do not commit them.

7. Verify, commit, and push from the isolated worktree.

```bash
git status --short
git diff --check
git add <intended-paths>
git commit -m "<clear imperative subject>"
git push -u origin <prefix>/<short-slug>
```

8. Remove the worktree after the branch is pushed or merged and no active agent
depends on it.

```bash
git worktree remove ../worktrees/<repo>-<short-slug>
```

## Do Not

- Do not switch branches in a checkout with unrelated active work.
- Do not use `git stash` when other agents may depend on the same checkout.
- Do not use `git reset --hard`, `git checkout --`, or destructive cleanup
  commands unless explicitly requested.
- Do not stage unrelated files just because they are present.
