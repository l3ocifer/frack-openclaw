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

## Resolving an upstream merge conflict

When `git merge upstream/main` reports a conflict in a file we patch:

1. Identify the patch from the list below
2. Re-apply it to the merged result
3. Bump `Last applied` for that patch
4. Commit with message `merge: upstream <sha> + reapply <patch-id>`
