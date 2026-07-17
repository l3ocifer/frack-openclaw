# Local patches vs upstream openclaw/openclaw

Track non-additive changes (anything outside `homelab/`). Additive
changes — files added under `homelab/` — don't need entries.

## Active patches

### a2a-gateway-ingress: native A2A JSON-RPC ingress on the gateway

- **Files**: `src/gateway/server-http.ts`, `src/gateway/server-runtime-state.ts`, `src/gateway/server.impl.ts`
- **Reason**: exposes `/.well-known/agent-card.json`, `/a2a` and
  `/a2a/v1/*` on the gateway HTTP server and threads an optional
  `handleA2aRequest` provider through runtime state, so the agent-bus
  and cross-agent handoffs can reach Frack natively without a sidecar.
- **Upstream PR**: not submitted (homelab-specific substrate).
- **Last applied**: 2026-07-17 against upstream@db3213264a6
  (`merge: upstream openclaw @ db3213264a6 + reapply a2a-gateway-ingress`).

## Resolving an upstream merge conflict

When `git merge upstream/main` reports a conflict in a file we patch:

1. Identify the patch from the list below
2. Re-apply it to the merged result
3. Bump `Last applied` for that patch
4. Commit with message `merge: upstream <sha> + reapply <patch-id>`
