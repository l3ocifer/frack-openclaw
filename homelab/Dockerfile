# frack-openclaw/homelab/Dockerfile
#
# Builds the OpenClaw image for **Frack**, the businesses agent in
# Leo's homelab. The build context is the repository root (this fork
# of openclaw/openclaw) — the upstream TypeScript source is at the
# repo root, plus any patches we've layered on top.
#
# Mirrors upstream's build approach (pnpm + bun) but trims the
# multi-stage chain to keep this homelab/Dockerfile readable.
# Upstream's full canonical Dockerfile lives at the repo root and
# is the reference. When upstream's build steps change, sync them
# here and bump CHANGELOG.md.
#
# Build (from repo root):
#   docker build -f homelab/Dockerfile \
#     -t ghcr.io/l3ocifer/frack-openclaw:latest \
#     -t ghcr.io/l3ocifer/frack-openclaw:$(git rev-parse --short HEAD) .

# syntax=docker/dockerfile:1.7

# ─── Stage 1: build ──────────────────────────────────────────────────
# Base images come from the ECR mirror rather than Docker Hub, matching
# puck-openclaw. Hub's anonymous pull limit is shared across every runner
# on this cluster's egress IP, so a burst of concurrent builds fails here
# with `toomanyrequests` and nothing gets pushed — which is indistinguishable
# from "the build never ran" unless you go read the Actions log.
FROM public.ecr.aws/docker/library/node:24.18.0-bookworm AS build

# Bun for build scripts (mirrors upstream)
RUN curl --retry 5 --retry-all-errors --retry-delay 2 -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"
RUN corepack enable

WORKDIR /app

# Copy lockfiles + workspace manifests first to maximize layer cache.
# Upstream's preinstall scripts and pnpm `patchedDependencies` resolve at
# install-time, so we must COPY everything pnpm peeks at BEFORE running
# `pnpm install`: workspace manifests, ui/package.json, patches/, scripts
# referenced by package.json's preinstall/postinstall hooks, and openclaw.mjs
# (declared as bin in package.json).
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml* tsconfig*.json* ./
COPY .npmrc .npmrc
COPY openclaw.mjs ./
COPY ui/package.json ./ui/package.json
COPY patches ./patches
COPY scripts ./scripts

RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    NODE_OPTIONS=--max-old-space-size=2048 \
    pnpm install --frozen-lockfile --prod=false

COPY . .

RUN pnpm build:docker || pnpm build
RUN pnpm ui:build || true

# Workspace packages (packages/*) are symlinked into node_modules by pnpm.
# The runtime stage copies node_modules but NOT the packages/ tree, so any
# workspace symlink left in place ships dangling and the gateway dies at
# startup with e.g. "Cannot find module '@openclaw/ai/internal/openai'"
# (2026-07-25 outage, seen on puck). Upstream's root Dockerfile materializes
# node_modules/@openclaw/ai the same way in its runtime-assets stage.
RUN set -eu; \
    for link in /app/node_modules/@openclaw/*; do \
      [ -L "$link" ] || continue; \
      target="$(readlink -f "$link")"; \
      case "$target" in /app/node_modules/*) continue ;; esac; \
      tmp="$(mktemp -d)"; \
      cp -a "$target" "$tmp/pkg"; \
      rm "$link"; \
      mv "$tmp/pkg" "$link"; \
      rmdir "$tmp"; \
    done
RUN node scripts/check-package-dist-imports.mjs /app

# ─── Stage 2: runtime ────────────────────────────────────────────────
FROM public.ecr.aws/docker/library/node:24.18.0-bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl wget tini \
      jq ripgrep git \
      postgresql-client \
      python3 python3-pip \
      gnupg lsb-release \
 && rm -rf /var/lib/apt/lists/*

# kubectl matched to current K3s cluster
ARG KUBECTL_VERSION=v1.34.0
RUN curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
      -o /usr/local/bin/kubectl \
 && chmod +x /usr/local/bin/kubectl

# Bitwarden CLI (`bw`) for the credential-lookup skill — talks to
# Vaultwarden (https://warden.leopaska.xyz). Persistent agent creds
# come in via SealedSecrets → envFrom; `bw` is here for ad-hoc lookups.
RUN apt-get update && apt-get install -y --no-install-recommends unzip && rm -rf /var/lib/apt/lists/*
ARG BW_VERSION=2026.4.1
RUN ARCH="$(dpkg --print-architecture)" \
 && case "$ARCH" in \
      amd64) BW_ARCH=linux ;; \
      arm64) BW_ARCH=linux-arm64 ;; \
      *) echo "unsupported arch: $ARCH" >&2; exit 1 ;; \
    esac \
 && curl -fsSL "https://github.com/bitwarden/clients/releases/download/cli-v${BW_VERSION}/bw-oss-${BW_ARCH}-${BW_VERSION}.zip" \
        -o /tmp/bw.zip \
 && unzip -q /tmp/bw.zip -d /usr/local/bin \
 && chmod +x /usr/local/bin/bw \
 && rm -f /tmp/bw.zip

# gh CLI for the github skill
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends gh \
 && rm -rf /var/lib/apt/lists/*

# Stripe CLI (read-only ops via API key but the CLI is convenient)
RUN curl -sL https://github.com/stripe/stripe-cli/releases/download/v1.21.8/stripe_1.21.8_linux_x86_64.tar.gz \
      | tar -xz -C /usr/local/bin stripe

# Copy built openclaw from the build stage. Upstream's binary is the
# bundled openclaw.mjs at the repo root; there is no compiled bin/ dir.
COPY --from=build /app/dist          /opt/openclaw/dist
COPY --from=build /app/node_modules  /opt/openclaw/node_modules
COPY --from=build /app/package.json  /opt/openclaw/package.json
COPY --from=build /app/openclaw.mjs  /opt/openclaw/openclaw.mjs
COPY --from=build /app/skills        /opt/openclaw/skills
# Workspace bootstrap templates (HEARTBEAT.md, etc.) are read from
# <packageRoot>/src/agents/templates at runtime (see
# src/agents/workspace-templates.ts). The bundle ships as dist/, so without
# this COPY the primary candidate /opt/openclaw/src/agents/templates is
# missing and every heartbeat tick fails "Missing workspace template".
COPY --from=build /app/src/agents/templates /opt/openclaw/src/agents/templates
# Redeploy 2026-06-25: rebuild after the A2A ingress handler restoration; the
# prior build-and-push run was preempted by a concurrent fleet fan-out.
RUN ln -sf /opt/openclaw/openclaw.mjs /usr/local/bin/openclaw \
 && chmod 755 /opt/openclaw/openclaw.mjs

# Fail the build if the copied node_modules contains dangling symlinks
# (i.e. a workspace package the materialization step above missed).
RUN broken="$(find /opt/openclaw/node_modules -xtype l)"; \
    if [ -n "$broken" ]; then \
      echo "dangling symlinks in runtime node_modules:" >&2; \
      echo "$broken" >&2; \
      exit 1; \
    fi

# Workspace skeleton — overlaid by mounted ConfigMaps + PVC at runtime
WORKDIR /opt/openclaw
RUN mkdir -p /root/.openclaw/workspace /root/.openclaw/skills /data

EXPOSE 18789

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -fsS http://localhost:18789/healthz || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["node", "/opt/openclaw/openclaw.mjs", "gateway", "--bind", "lan", "--port", "18789", "--allow-unconfigured"]

# ci: re-trigger homelab build 20260625T182233Z (warm-cache run; prior run reaped under fleet load)
