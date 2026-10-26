# Upstream sync — manual resolution required

Generated: 2026-10-26T08:00:15Z
Upstream:   https://github.com/openclaw/openclaw.git @ main (fetched from https://git.leopaska.xyz/leo/upstream-openclaw.git)
Upstream commit: aba19fb7b68045dd866f656a0d7415b036f4a7e3
Behind by:  47300 commits

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
git fetch origin "chore/upstream-sync-2026-10-26-aba19fb" && git switch "chore/upstream-sync-2026-10-26-aba19fb"
git remote add upstream https://git.leopaska.xyz/leo/upstream-openclaw.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
# resolve, then:
git rm UPSTREAM_SYNC_NOTES.md
git commit
git push --force origin "chore/upstream-sync-2026-10-26-aba19fb"
```

Then update the PR body / drop draft state and merge.
