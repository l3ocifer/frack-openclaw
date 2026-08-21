# Upstream sync — manual resolution required

Generated: 2026-08-21T08:00:11Z
Upstream:   https://github.com/openclaw/openclaw.git @ main
Upstream commit: dfce5f695871aa2230037fdfb024f4c75fd180ef
Behind by:  9050 commits

The automated 3-way merge on top of `origin/main` produced conflicts.
The merge was aborted before any conflict markers were committed, so
this branch currently contains only this notes file on top of
`origin/main` — that is by design.

## Conflicting paths

```
.github/CODEOWNERS
src/gateway/server-http.ts
src/gateway/server-runtime-state-prepare.ts
src/gateway/server-runtime-state.ts
```

## How to resolve

```bash
git fetch origin "chore/upstream-sync-2026-08-21-dfce5f6" && git switch "chore/upstream-sync-2026-08-21-dfce5f6"
git remote add upstream https://github.com/openclaw/openclaw.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
# resolve, then:
git rm UPSTREAM_SYNC_NOTES.md
git commit
git push --force origin "chore/upstream-sync-2026-08-21-dfce5f6"
```

Then update the PR body / drop draft state and merge.
