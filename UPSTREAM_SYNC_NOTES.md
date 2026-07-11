# Upstream sync — manual resolution required

Generated: 2026-07-11T08:00:21Z
Upstream:   https://github.com/openclaw/openclaw.git @ main
Upstream commit: f9ebefba29a0b4a29a2389694f84ed7c95014b8a
Behind by:  3920 commits

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
git fetch origin "chore/upstream-sync-2026-07-11-f9ebefb" && git switch "chore/upstream-sync-2026-07-11-f9ebefb"
git remote add upstream https://github.com/openclaw/openclaw.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
# resolve, then:
git rm UPSTREAM_SYNC_NOTES.md
git commit
git push --force origin "chore/upstream-sync-2026-07-11-f9ebefb"
```

Then update the PR body / drop draft state and merge.
