# Upstream sync — manual resolution required

Generated: 2026-05-15T03:09:37Z
Upstream:   https://github.com/openclaw/openclaw.git @ main
Upstream commit: 346a773b189470d5d7f4639e17024c048c213abb
Behind by:  865 commits

The automated 3-way merge on top of `origin/main` produced conflicts.
The merge was aborted before any conflict markers were committed, so
this branch currently contains only this notes file on top of
`origin/main` — that is by design.

## Conflicting paths

```
CHANGELOG.md
docs/.generated/config-baseline.sha256
docs/.generated/plugin-sdk-api-baseline.sha256
docs/cli/plugins.md
docs/plugins/plugin-inventory.md
docs/reference/test.md
extensions/codex/src/app-server/run-attempt.ts
extensions/codex/src/app-server/session-binding.ts
extensions/codex/src/app-server/thread-lifecycle.ts
extensions/codex/src/app-server/thread-lifecycle.user-mcp-servers.test.ts
extensions/codex/src/migration/apply.ts
extensions/codex/src/migration/plan.ts
extensions/telegram/src/channel.gateway.test.ts
extensions/whatsapp/package.json
package.json
pnpm-lock.yaml
pnpm-workspace.yaml
scripts/check-dependency-pins.mjs
scripts/lib/plugin-sdk-private-local-only-subpaths.json
scripts/test-live-cli-backend-docker.sh
src/acp/control-plane/manager.core.ts
src/acp/control-plane/manager.test.ts
src/agents/pi-embedded-runner/run/failover-policy.ts
src/agents/session-tool-result-guard.ts
src/cli/config-cli.ts
src/cli/plugins-install-record-commit.ts
src/commands/migrate/output.test.ts
src/commands/migrate/output.ts
src/commands/migrate/types.ts
src/config/config.ts
src/config/mutate.ts
src/cron/isolated-agent.session-identity.test.ts
src/cron/isolated-agent/run-executor.ts
src/cron/isolated-agent/run.session-key-isolation.test.ts
src/gateway/chat-abort.test.ts
src/gateway/chat-abort.ts
src/gateway/client.test.ts
src/gateway/server-chat-state.ts
src/gateway/server-chat.ts
src/gateway/server-maintenance.test.ts
src/gateway/server-maintenance.ts
src/gateway/server-methods/agent.test.ts
src/gateway/server-methods/chat.abort.test-helpers.ts
src/gateway/server-methods/chat.directive-tags.test.ts
src/gateway/server-methods/chat.ts
src/gateway/server-methods/shared-types.ts
src/gateway/server-plugins.ts
src/gateway/server-request-context.test.ts
src/gateway/server-request-context.ts
src/gateway/server-startup-early.test.ts
src/gateway/server.impl.ts
src/gateway/server.node-invoke-approval-bypass.test.ts
src/gateway/server.sessions-send.test.ts
src/gateway/talk-realtime-relay.test.ts
src/infra/npm-managed-root.test.ts
src/infra/npm-managed-root.ts
src/media-understanding/shared.test.ts
src/media-understanding/shared.ts
src/media/fetch.test.ts
src/media/fetch.ts
src/media/web-media.ts
src/plugins/git-install.test.ts
src/plugins/install.npm-spec.e2e.test.ts
src/plugins/install.npm-spec.test.ts
src/plugins/install.ts
src/plugins/provider-auth-choice.ts
src/plugins/registry.runtime-config.test.ts
src/plugins/registry.ts
src/wizard/setup.post-install-migration.test.ts
src/wizard/setup.post-install-migration.ts
test/scripts/bundled-plugin-build-entries.test.ts
test/scripts/check-dependency-pins.test.ts
ui/src/ui/chat/build-chat-items.ts
```

## How to resolve

```bash
git fetch origin "chore/upstream-sync-2026-05-15-346a773" && git switch "chore/upstream-sync-2026-05-15-346a773"
git remote add upstream https://github.com/openclaw/openclaw.git 2>/dev/null || true
git fetch upstream main
git merge upstream/main
# resolve, then:
git rm UPSTREAM_SYNC_NOTES.md
git commit
git push --force origin "chore/upstream-sync-2026-05-15-346a773"
```

Then update the PR body / drop draft state and merge.
