# Upstream sync — manual resolution required

Generated: 2026-09-01T08:00:03Z
Upstream:   https://github.com/openclaw/openclaw.git @ main
Upstream commit: 0434e079596f9f912e321aede2551866fcf6d4ee
Behind by:  13755 commits

The automated 3-way merge on top of `origin/main` produced conflicts.
The merge was aborted before any conflict markers were committed, so
this branch currently contains only this notes file on top of
`origin/main` — that is by design.

## Conflicting paths

```
.github/CODEOWNERS
src/agents/agent-tools.cron-scope.test.ts
src/gateway/server-http.ts
src/gateway/server-runtime-state-prepare.ts
src/gateway/server-runtime-state.ts
```

## How to resolve

```bash
git fetch origin "chore/upstream-sync-2026-09-01-0434e07" && git switch "chore/upstream-sync-2026-09-01-0434e07"
git remote add upstream https://github.com/openclaw/openclaw.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
# resolve, then:
git rm UPSTREAM_SYNC_NOTES.md
git commit
git push --force origin "chore/upstream-sync-2026-09-01-0434e07"
```

Then update the PR body / drop draft state and merge.
