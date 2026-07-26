# Local patches vs upstream openclaw/openclaw

Track non-additive changes (anything outside `homelab/`). Additive
changes — files added under `homelab/` — don't need entries.

## Active patches

### a2a-gateway-ingress: native A2A JSON-RPC ingress on the gateway

- **Files**: `src/gateway/server-a2a-ingress.ts` (additive — holds the whole
  implementation), plus three wiring points:
  `src/gateway/server-http.ts` (`isA2aPath` + the `a2a` stage),
  `src/gateway/server-runtime-state.ts` (optional `handleA2aRequest` param),
  `src/gateway/server-runtime-state-prepare.ts` (one call passing the handler
  into `createGatewayRuntimeState`).
- **Reason**: exposes `/.well-known/agent-card.json`, `/a2a` and
  `/a2a/v1/*` on the gateway HTTP server and threads an optional
  `handleA2aRequest` provider through runtime state, so the agent-bus
  and cross-agent handoffs can reach Frack natively without a sidecar.
- **Upstream PR**: not submitted (homelab-specific substrate).
- **Last applied**: 2026-07-26 against upstream@dfcd3b9e0b0.
- **2026-07-26 restructure**: upstream split `server.impl.ts` into
  `server-public.ts` + `server-start.ts` + `server-startup-*.ts`, leaving a
  thin re-export facade. The implementation used to live inline in
  `server.impl.ts`, so that split conflicted the entire file. It now lives in
  its own additive module and the patch is one wiring line, which should stop
  future upstream refactors of the startup path from conflicting. This also
  guards against the silent-drop failure mode: the handler was lost in an
  earlier sync (last present in cc0065d3b2) while the routing stayed behind,
  so inbound `POST /a2a/v1/message:send` 404'd and missions never reached a
  turn. The handler now resolves the gateway request context per request and
  answers 503 while the gateway is still starting, instead of capturing a
  local that only exists late in startup.

### homelab-config-validator: pre-push schema check for openclaw.json

- **Files**: `homelab/scripts/validate-config.mts` (additive, inside `homelab/`
  — listed here for discoverability, not because it conflicts).
- **Reason**: the gateway validates its config against a _strict_ zod schema and
  exits non-zero on an unknown key, so a key upstream renames or retires becomes
  a CrashLoopBackOff that only shows up after the image builds and rolls. Run it
  after every upstream merge and before pushing.
- **Run**: `./node_modules/.bin/tsx homelab/scripts/validate-config.mts`

## Config schema migrations (homelab/config/openclaw.json)

Not source patches, but the same upstream-drift hazard, and the reason the
validator above exists.

### 2026-07-26 (upstream@dfcd3b9e0b0)

Puck hit this first — it crash-looped 7 times on the new image with
`Invalid config … Unrecognized keys`. Frack carried the identical keys and was
only still up because it had not yet rolled onto the new image, so the same
three changes were applied here pre-emptively:

- `agents.defaults.compaction.reserveTokens` / `reserveTokensFloor` — **removed,
  no replacement.** Upstream deleted the projection-reserve mechanism they fed
  (no `DEFAULT_PROJECTION_RESERVE_TOKENS` remains in the tree) and put both keys
  on the retired-knob list that `openclaw doctor --fix` strips. They were never
  the effective lever here anyway: verified live 2026-06-25 that the mid-turn
  overflow precheck read its own 16384 reserve from `settings.json` regardless.
  If prompt-budget starvation returns, `compaction.keepRecentTokens` is the
  modern lever.
- `agents.defaults.memorySearch` → **root `memory.search`.** The owner moved to
  the root (per-agent overrides now live at `agents.entries.<id>.memory.search`;
  `agents.defaults` does not accept it at all). Three sub-blocks are gone with no
  replacement and were dropped rather than translated: `store.driver` (sqlite is
  the only driver), the whole `sync` block (watch / debounce / onSessionStart /
  onSearch are no longer configurable — indexing is driven internally), and
  `query.hybrid` (hybrid retrieval is always on; `query` now takes only
  `maxResults` and `minScore`).
- `agents.list[]` → `agents.entries{}`. The array form still loads via a doctor
  migration, so this one was not fatal; written canonically anyway so the seeded
  ConfigMap does not need a migration pass on every boot.

## Resolving an upstream merge conflict

When `git merge upstream/main` reports a conflict in a file we patch:

1. Identify the patch from the list below
2. Re-apply it to the merged result
3. Bump `Last applied` for that patch
4. Commit with message `merge: upstream <sha> + reapply <patch-id>`
5. Run `./node_modules/.bin/tsx homelab/scripts/validate-config.mts` before
   pushing — a clean merge does not mean the config still matches the schema
