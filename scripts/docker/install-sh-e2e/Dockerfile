# syntax=docker/dockerfile:1.7

FROM node:24-bookworm-slim@sha256:2c87ef9bd3c6a3bd4b472b4bec2ce9d16354b0c574f736c476489d09f560a203

RUN --mount=type=cache,id=openclaw-install-sh-e2e-apt-cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,id=openclaw-install-sh-e2e-apt-lists,target=/var/lib/apt,sharing=locked \
  apt-get update \
  && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    git

COPY install-sh-common/version-parse.sh /usr/local/install-sh-common/version-parse.sh
COPY --chmod=755 install-sh-e2e/run.sh /usr/local/bin/openclaw-install-e2e

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

ENTRYPOINT ["/usr/local/bin/openclaw-install-e2e"]
