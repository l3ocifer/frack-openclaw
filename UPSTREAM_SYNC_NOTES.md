# Upstream sync — manual resolution required

Generated: 2026-07-12T08:00:29Z
Upstream:   https://github.com/openclaw/openclaw.git @ main
Upstream commit: d325b6c76b08dfd54c1305c0136d4308382a5512
Behind by:  4520 commits

The automated 3-way merge on top of `origin/main` produced conflicts.
The merge was aborted before any conflict markers were committed, so
this branch currently contains only this notes file on top of
`origin/main` — that is by design.

## Conflicting paths

```
.github/pull_request_template.md
AGENTS.md
extensions/imessage/src/monitor/monitor-provider.ts
src/gateway/server-http.ts
src/gateway/server-runtime-state.ts
src/gateway/server.impl.ts
src/infra/device-bootstrap.test.ts
src/pairing/setup-code.test.ts
```

## How to resolve

```bash
git fetch origin "chore/upstream-sync-2026-07-12-d325b6c" && git switch "chore/upstream-sync-2026-07-12-d325b6c"
git remote add upstream https://github.com/openclaw/openclaw.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
# resolve, then:
git rm UPSTREAM_SYNC_NOTES.md
git commit
git push --force origin "chore/upstream-sync-2026-07-12-d325b6c"
```

Then update the PR body / drop draft state and merge.
