# Upstream sync — manual resolution required

Generated: 2026-10-08T08:03:48Z
Upstream:   https://github.com/openclaw/openclaw.git @ main (fetched from https://git.leopaska.xyz/leo/upstream-openclaw.git)
Upstream commit: 6dd7b2e00b3edaf07383052660f2cb8cddf8575d
Behind by:  34121 commits

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
git fetch origin "chore/upstream-sync-2026-10-08-6dd7b2e" && git switch "chore/upstream-sync-2026-10-08-6dd7b2e"
git remote add upstream https://git.leopaska.xyz/leo/upstream-openclaw.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
# resolve, then:
git rm UPSTREAM_SYNC_NOTES.md
git commit
git push --force origin "chore/upstream-sync-2026-10-08-6dd7b2e"
```

Then update the PR body / drop draft state and merge.
