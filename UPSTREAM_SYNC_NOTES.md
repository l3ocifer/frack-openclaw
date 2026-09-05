# Upstream sync — manual resolution required

Generated: 2026-09-05T08:01:33Z
Upstream:   https://github.com/openclaw/openclaw.git @ main
Upstream commit: a2fedfb837db95d05f0fc3ae3ce5a24cc1bef085
Behind by:  15966 commits

The automated 3-way merge on top of `origin/main` produced conflicts.
The merge was aborted before any conflict markers were committed, so
this branch currently contains only this notes file on top of
`origin/main` — that is by design.

## Conflicting paths

```
.github/CODEOWNERS
.github/workflows/openclaw-npm-release.yml
src/agents/agent-tools.cron-scope.test.ts
src/gateway/server-http.ts
src/gateway/server-runtime-state-prepare.ts
src/gateway/server-runtime-state.ts
```

## How to resolve

```bash
git fetch origin "chore/upstream-sync-2026-09-05-a2fedfb" && git switch "chore/upstream-sync-2026-09-05-a2fedfb"
git remote add upstream https://github.com/openclaw/openclaw.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
# resolve, then:
git rm UPSTREAM_SYNC_NOTES.md
git commit
git push --force origin "chore/upstream-sync-2026-09-05-a2fedfb"
```

Then update the PR body / drop draft state and merge.
