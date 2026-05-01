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
FROM node:24-bookworm AS build

# Bun for build scripts (mirrors upstream)
RUN curl --retry 5 --retry-all-errors --retry-delay 2 -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"
RUN corepack enable

WORKDIR /app

# Copy lockfiles + workspace manifests first to maximize layer cache
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml* tsconfig*.json* ./
COPY .npmrc .npmrc

# Pnpm install — mirrors upstream's install step. If upstream gains
# additional workspace globs, sync via the upstream-sync workflow.
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile --prod=false

# Copy the rest of the source. We exclude homelab/ via .dockerignore
# so the cache key for source-only changes stays clean.
COPY . .

# Build dist/ — `pnpm build` is upstream's canonical task
RUN pnpm build && pnpm ui:build || true

# ─── Stage 2: runtime ────────────────────────────────────────────────
FROM node:24-bookworm-slim

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

# 1Password CLI for the `op` skill
RUN curl -sSfO https://downloads.1password.com/linux/keys/1password.asc \
 && gpg --dearmor 1password.asc \
 && mv 1password.asc.gpg /usr/share/keyrings/1password-archive-keyring.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" \
      > /etc/apt/sources.list.d/1password.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends 1password-cli \
 && rm -rf /var/lib/apt/lists/* 1password.asc

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

# Copy built openclaw from the build stage
COPY --from=build /app/dist                /opt/openclaw/dist
COPY --from=build /app/node_modules        /opt/openclaw/node_modules
COPY --from=build /app/package.json        /opt/openclaw/package.json
COPY --from=build /app/bin                 /opt/openclaw/bin
RUN ln -sf /opt/openclaw/bin/openclaw /usr/local/bin/openclaw \
 && chmod +x /opt/openclaw/bin/openclaw

# Workspace skeleton — overlaid by mounted ConfigMaps + PVC at runtime
WORKDIR /root
RUN mkdir -p /root/.openclaw/workspace /root/.openclaw/skills /data

EXPOSE 18789

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -fsS http://localhost:18789/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["openclaw", "gateway", "wake", "--foreground", "--port=18789", "--bind=0.0.0.0"]
