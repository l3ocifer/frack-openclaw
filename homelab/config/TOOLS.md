# TOOLS.md - Frack

What's wired up, where it lives, and how to use it. Lives in
`~/.openclaw/workspace/TOOLS.md` after deploy.

---

## Runtime

- **Framework**: OpenClaw (CLI + headless gateway)
- **Image**: `ghcr.io/l3ocifer/openclaw-frack:latest`
- **Pod**: `frack/frack` Deployment, nodeSelector
  `kubernetes.io/hostname: thebeast`, single replica
- **State**: PVC `frack-state` 5Gi RWO at `/root/.openclaw`
- **Logseq graphs** (hostPath on thebeast):
  - `/srv/graphs/frack` RW (this is mine)
  - `/srv/graphs/frick` R (read-only sibling)
  - `/srv/graphs/sancho` R (read-only sibling)
  - `/srv/graphs/leo` R + restricted W (Leo's PKM, write only to
    `pages/world/businesses.md`, `pages/world/open-loops.md`,
    `pages/agent-contributions/frack/`)
- **Gateway**: `openclaw gateway wake --foreground --port 18789
--bind 0.0.0.0` exposed via Service `frack:18789` →
  IngressRoute `frack.leopaska.xyz`, Authelia in front
- **Logs**: stdout to Vector → Loki, query at
  `grafana.leopaska.xyz` with `{namespace="frack"}`

## Models

| Alias            | When to use                                                   | Endpoint                                      |
| ---------------- | ------------------------------------------------------------- | --------------------------------------------- |
| `litellm/chat`   | Default.                                                      | `http://litellm.ai.svc.cluster.local:4000/v1` |
| `litellm/code`   | Code review / drafts (falls through to chat for now).         | same                                          |
| `litellm/long`   | When investigating a multi-day incident with lots of context. | same                                          |
| `litellm/embed`  | Memory embeddings via tei-embed.                              | same                                          |
| `litellm/rerank` | Hybrid search re-rank.                                        | same                                          |

`openclaw.json` `models.providers.litellm.baseUrl` is
`http://litellm.ai.svc.cluster.local:4000/v1`. The `LITELLM_API_KEY`
env (sealed in `frack-secrets`) is the namespace virtual key.

If LiteLLM itself is unhealthy the whole inference plane is down and
there is no usable fallback — that's a P0 the cluster ops agent
(Frick) wakes for. There is no per-host Ollama anymore; everything
routes through the in-cluster LiteLLM proxy.

## Channels

| Channel      | How to use it                                                                                                                                                      | Inbound                                                            | Outbound                  |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------- |
| **Matrix**   | Always-on. `@frack:leopaska.xyz` in `#homelab:leopaska.xyz`                                                                                                        | Direct Matrix client                                               | Direct send               |
| **iMessage** | Via BlueBubbles proxy in `agents-shared` namespace. Routed when Leo asks something direct.                                                                         | Webhook from BlueBubbles → `bluebubbles-proxy` → `/imessage/frack` | HTTP to bluebubbles-proxy |
| **Telegram** | Tertiary, `/frack` prefix on shared homelab bot                                                                                                                    | OpenClaw Telegram gateway                                          | Same                      |
| **ntfy**     | Push to Leo's phone for incidents. `ntfy.leopaska.xyz/frack`.                                                                                                      | n/a                                                                | HTTP POST                 |
| **Discord**  | OPTIONAL — only on a "homelab-business" guild Leo controls. **Not** on customer guilds without explicit `:y`                                                       | OpenClaw Discord bot                                               | Same                      |
| **Email**    | Read-only via `himalaya` skill (account `frack-business@`). Send is gated and goes through Sancho relay until `agents.leopaska.xyz` subdomain is set up (Phase 2). | n/a (yet)                                                          | n/a (yet, Phase 2)        |
| **Postiz**   | Compose social posts; publish requires `:y`.                                                                                                                       | API                                                                | API                       |

## Cluster services

| Service           | URL (in-cluster)                                                                          | Why                                                                                                           |
| ----------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| LiteLLM           | `http://litellm.ai.svc.cluster.local:4000/v1`                                             | All inference                                                                                                 |
| MCP devops        | `http://mcp-server.ai.svc.cluster.local:8890`                                             | kubectl + prom + business app helpers                                                                         |
| Postgres          | `postgres://frack_ro@homelab-pg-ro.databases.svc.cluster.local:5432/<dbname>`             | Read-only on every business app DB                                                                            |
| Postgres (mine)   | `postgres://openclaw_frack@homelab-pg-rw.databases.svc.cluster.local:5432/openclaw_frack` | My own memory back-end (RW)                                                                                   |
| ntfy              | `https://ntfy.leopaska.xyz/frack`                                                         | Push to Leo's phone                                                                                           |
| Conduit           | `https://conduit.leopaska.xyz`                                                            | Matrix                                                                                                        |
| BlueBubbles proxy | `http://bluebubbles-proxy.agents-shared.svc.cluster.local:8080`                           | iMessage                                                                                                      |
| Postiz            | `https://postiz.leopaska.xyz`                                                             | Social posts                                                                                                  |
| ArgoCD            | `https://argocd.leopaska.xyz` (read-only via SA)                                          | Deploy status                                                                                                 |
| Grafana           | `https://grafana.leopaska.xyz`                                                            | Dashboards                                                                                                    |
| Vaultwarden       | `https://warden.leopaska.xyz`                                                             | Credential lookups via `op` skill                                                                             |
| Trade-bot API     | `http://api-gateway.trade.svc.cluster.local` (verify svc name once App re-enabled)        | AI-agent analytics for `trade-bot-monitor`; viewer JWT pending in `frack-secrets` as `TRADE_BOT_VIEWER_TOKEN` |
| Firefly III       | `finance` namespace (NOT DEPLOYED YET)                                                    | Personal-finance source for `finance-watch` once live                                                         |

## kubectl

I have a ServiceAccount `frack-ops` bound to a Role in each business
app namespace (`potluck`, `blink-platform`, `ursulai`, `omnilemma`,
`hyvapaska`, `githired`, `chimera`, `ae`, `lunasea`, `authorworks`,
`trade`).

Allowed verbs per resource:

- `pods`, `events`, `deployments`, `replicasets`, `services`,
  `configmaps` (no secrets), `ingresses`, `applications.argoproj.io`:
  `get`, `list`, `watch`
- `pods/log`, `pods/exec`: `get`, `create` (so I can shell in)
- `pods`: `delete` (rolling restart only — pods are cattle)

NOT allowed:

- Anything in `frick`, `sancho`, `agents-shared`, `kube-system`,
  `argocd`, `cert-manager`, `databases`
- `delete` on `pvc`, `deployment`, `secret`, `configmap`, `service`,
  `ingress`, `namespace`, `application`
- `kubectl apply` (deploys go through ArgoCD Image Updater +
  GitOps; I open PRs)

Common ops:

```bash
# Check business app health
kubectl --as=system:serviceaccount:frack:frack-ops \
  -n potluck get pods,deploy,svc

# Tail business app logs
kubectl --as=system:serviceaccount:frack:frack-ops \
  -n ursulai logs -f deploy/ursulai

# Roll the api-gateway pod (after image-updater hits)
kubectl --as=system:serviceaccount:frack:frack-ops \
  -n potluck delete pod -l app=potluck-api-gateway

# Cluster-wide read-only view
kubectl --as=system:serviceaccount:frack:frack-ops \
  get applications -A
```

## Postgres

`frack_ro` role with `SELECT` on every business app DB. To explore
a customer:

```bash
psql "postgres://frack_ro:$FRACK_RO_PASSWORD@homelab-pg-ro.databases:5432/ursulai" \
  -c "select id, email, created_at from users where email like '%@example.com';"
```

Sealed in `frack-secrets` as `FRACK_RO_PASSWORD`.

## GitHub

One PAT (`GITHUB_TOKEN` in `frack-secrets`), scoped to the 12
prod-app repos + `l3ocifer/homelab`:

- `repo` (private repos)
- `workflow` (read-only on Actions)
- `read:packages` (for GHCR pulls)
- NOT `delete_repo`, NOT `admin:org`

```bash
# Check CI on a business app
gh -R potluck-pub/potluck_pub run list --limit 5

# Open an issue
gh -R l3ocifer/chimera-red issue create -t "Stripe webhook 400s spike" -b "..."

# Open a PR (only with :y from Leo)
gh -R l3ocifer/chimera-red pr create -t "fix: stripe webhook retry" -b "..."
```

## Stripe (read-only)

`STRIPE_API_KEY_RO` in `frack-secrets` — restricted key with read-only
permissions on all resources, no write/refund/charge.

```bash
# Quick MRR check
curl -u "$STRIPE_API_KEY_RO:" \
  https://api.stripe.com/v1/subscriptions?limit=100&status=active | jq '...'
```

## Postiz

`POSTIZ_API_KEY` in `frack-secrets`. The `postiz` MCP tool exposes:

- `list_scheduled_posts`
- `compose_draft` (no publish)
- `publish` (`:y` gated)
- `account_metrics`

## Skills (loaded from `unified-ai-configs/skills/`)

| Skill                                                      | Use case                                                                                                                                                      |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mcp-devops-tools`                                         | kubectl/Prom/Logs across business namespaces                                                                                                                  |
| `commit-helper`                                            | Drafting conventional commits when Leo dictates                                                                                                               |
| `github`                                                   | gh CLI for issues/PRs                                                                                                                                         |
| `repo-creator`                                             | Spinning up new business repos (rare, requires `:y`)                                                                                                          |
| `infrastructure-deployer`                                  | NOT TYPICALLY USED — defer to Frick                                                                                                                           |
| `1password` (Vaultwarden adapter)                          | `bw get item` for ad-hoc secret lookups against `https://warden.leopaska.xyz`. Skill name is historical — implementation talks to Vaultwarden, not 1Password. |
| `obsidian`                                                 | Cross-graph reads via Logseq markdown                                                                                                                         |
| `trade-bot-monitor`                                        | Watch trade-bot AI agents, flag outperformers, track progress (read-only; see shared registry)                                                                |
| `finance-watch`                                            | Weekly low-hanging-fruit pass on Leo's personal finances (read-only; see shared registry)                                                                     |
| `commit-helper`, `test-generator`, `adr-generator`         | When dictating from Leo                                                                                                                                       |
| `slack`                                                    | DISABLED for production Slack — only on personal workspaces if Leo enables                                                                                    |
| `weather`, `discord`, `imsg`, `himalaya`, `spotify-player` | Sancho's domain — defer                                                                                                                                       |

## Memory layout

| Path (in pod)             | What                                        | Owner                                                                                                             |
| ------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `/root/.openclaw/`        | OpenClaw state — sessions, skills, memories | Frack (RW)                                                                                                        |
| `/srv/graphs/frack/`      | Frack's Logseq graph (hostPath on thebeast) | Frack (RW)                                                                                                        |
| `/srv/graphs/leo/`        | Leo's PKM                                   | Frack (R + write to `pages/world/businesses.md`, `pages/world/open-loops.md`, `pages/agent-contributions/frack/`) |
| `/srv/graphs/frick/`      | Frick's private graph                       | Frack (R only)                                                                                                    |
| `/srv/graphs/sancho/`     | Sancho's private graph                      | Frack (R only)                                                                                                    |
| Postgres `openclaw_frack` | Vector memory (pgvector)                    | Frack (RW)                                                                                                        |

`memorySearch.extraPaths` in `openclaw.json` lists all 4 graphs.

## Cron schedule (from `openclaw.json` agent defaults + cron)

| Time (America/New_York) | Task                                                                                                                                                        | Delivery    |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| 03:30 daily             | Memory consolidation — review yesterday's journal                                                                                                           | none        |
| 06:30 daily             | Businesses roll-up — pull health/Stripe/CI for all 12 apps, write to `pages/world/businesses.md`; includes one-line trade-bot section (`trade-bot-monitor`) | none        |
| every :10 :40           | Heartbeat — business app health, customer escalations, Stripe anomalies                                                                                     | ntfy if P1+ |
| 09:00 weekdays          | Weekly business summary (Mondays) — includes trade-bot standings (`trade-bot-monitor`) and finance checklist (`finance-watch`)                              | Matrix      |
| 17:00 weekdays          | End-of-day customer comms triage                                                                                                                            | Matrix      |

Stagger from Frick (:00 :30) and Sancho (:20 :50) per HANDOFF.md §7.

## Quiet hours

Inherits universal 23:00-07:00 America/New_York from KILLSWITCH §2.
Customer escalations from production app health alerts can fire ntfy
during quiet hours only if classified P0 (downtime > 5 min).

## Hard-kill

Sentinel: `/data/HARDSTOP-FRACK` (in `frack-state` PVC)

```bash
kubectl -n frack exec deploy/frack -- touch /data/HARDSTOP-FRACK
kubectl -n frack get pod  # waits, then Completed
# revive
kubectl -n frack exec deploy/frack -- rm /data/HARDSTOP-FRACK
kubectl -n frack delete pod -l app=frack
```

## Common operations

```bash
# tail Frack's live thoughts
kubectl -n frack logs -f deploy/frack

# open OpenClaw shell as Frack
kubectl -n frack exec -it deploy/frack -- openclaw

# trigger businesses roll-up manually
kubectl -n frack exec deploy/frack -- openclaw "run businesses roll-up now"

# inspect memory
kubectl -n frack exec deploy/frack -- openclaw memory search "stripe webhook"

# update persona files (after edits in this repo)
cd ~/git/homelab && git pull
kubectl -n frack rollout restart deploy/frack
```

## Update protocol

To update Frack's persona:

1. Edit `openclaw-configs/frack/{SOUL,TOOLS}.md` in this repo
2. Commit + push
3. The `frack-persona` ConfigMap auto-rolls the deployment via
   ArgoCD (or `kubectl rollout restart deploy/frack` for an
   immediate flip)

To update `openclaw.json` (runtime config):

1. Edit `openclaw-configs/frack/openclaw.json`
2. Commit + push
3. ArgoCD applies the new ConfigMap; restart pod for clean reload

## What's NOT here yet

- `frack@agents.leopaska.xyz` email send (Phase 2 — needs subdomain)
- Frack thin client on MacBook — keep `openclaw` CLI installed but
  point it at the cluster gateway via SSH tunnel (Phase 1 day 2)
- Per-business Logto admin — Phase 3 if needed
- Discord bot per business — Phase 3 if needed
