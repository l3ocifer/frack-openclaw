# Upstream sync — manual resolution required

Generated: 2026-10-06T08:05:27Z
Upstream:   https://github.com/openclaw/openclaw.git @ main (fetched from https://git.leopaska.xyz/leo/upstream-openclaw.git)
Upstream commit: 8371bb89c8a76fea9c1598c73cc7484652edc1ff
Behind by:  33475 commits

The automated 3-way merge on top of `origin/main` produced conflicts.
The merge was aborted before any conflict markers were committed, so
this branch currently contains only this notes file on top of
`origin/main` — that is by design.

## Conflicting paths

```
.agents/skills/autoreview/tests/test_autoreview_hardening.py
.github/CODEOWNERS
.github/workflows/openclaw-npm-release.yml
extensions/telegram/src/polling-session.test.ts
src/agents/agent-tools.cron-scope.test.ts
src/agents/embedded-agent-subscribe.handlers.tools.media.test.ts
src/gateway/server-http.ts
src/gateway/server-runtime-state-prepare.ts
src/gateway/server-runtime-state.ts
test/scripts/openclaw-test-state.test.ts
```

## How to resolve

```bash
git fetch origin "chore/upstream-sync-2026-10-06-8371bb8" && git switch "chore/upstream-sync-2026-10-06-8371bb8"
git remote add upstream https://git.leopaska.xyz/leo/upstream-openclaw.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
# resolve, then:
git rm UPSTREAM_SYNC_NOTES.md
git commit
git push --force origin "chore/upstream-sync-2026-10-06-8371bb8"
```

Then update the PR body / drop draft state and merge.
