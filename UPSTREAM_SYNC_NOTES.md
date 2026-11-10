# Upstream sync — manual resolution required

Generated: 2026-11-10T09:00:13Z
Upstream:   https://github.com/openclaw/openclaw.git @ main (fetched from https://git.leopaska.xyz/leo/upstream-openclaw.git)
Upstream commit: 19aa98b9258b8b7066de53a8c97c96834f42fec3
Behind by:  55039 commits

The automated 3-way merge on top of `origin/main` produced conflicts.
The merge was aborted before any conflict markers were committed, so
this branch currently contains only this notes file on top of
`origin/main` — that is by design.

## Conflicting paths

```
.agents/skills/autoreview/tests/test_autoreview_hardening.py
.github/CODEOWNERS
.github/workflows/openclaw-npm-release.yml
apps/linux/src-tauri/src/gateway_ws.rs
extensions/telegram/src/polling-session.test.ts
src/agents/agent-tools.cron-scope.test.ts
src/agents/embedded-agent-subscribe.handlers.tools.media.test.ts
src/gateway/server-http.ts
src/gateway/server-runtime-state-prepare.ts
src/gateway/server-runtime-state.ts
```

## How to resolve

```bash
git fetch origin "chore/upstream-sync-2026-11-10-19aa98b" && git switch "chore/upstream-sync-2026-11-10-19aa98b"
git remote add upstream https://git.leopaska.xyz/leo/upstream-openclaw.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
# resolve, then:
git rm UPSTREAM_SYNC_NOTES.md
git commit
git push --force origin "chore/upstream-sync-2026-11-10-19aa98b"
```

Then update the PR body / drop draft state and merge.
