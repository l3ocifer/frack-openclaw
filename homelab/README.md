# Frack — OpenClaw businesses agent

This is **Leo's fork of [openclaw/openclaw](https://github.com/openclaw/openclaw)**,
extended with everything needed to run it as `Frack` (the agent that
runs Leo's 12 production businesses) inside [Leo's homelab K3s
cluster](https://github.com/l3ocifer/homelab).

The framework code itself lives at the repo root (it's a fork). All
homelab-specific additions live under `homelab/`. Upstream syncs via
`git fetch upstream && git merge upstream/main` (automated weekly by
`homelab/.github/workflows/upstream-sync.yml`).

## Layout

```
frack-openclaw/                      ← repo root (this fork)
├── (upstream openclaw source)
│   ├── src/
│   ├── extensions/
│   ├── ui/
│   ├── package.json
│   ├── pnpm-lock.yaml
│   └── ...
└── homelab/                          ← everything we add
    ├── Dockerfile                    ← multi-stage: pnpm build + runtime overlay
    ├── k8s/                          ← kustomize tree (ArgoCD pulls this path)
    │   ├── kustomization.yaml
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── ingressroute.yaml
    │   ├── pvc.yaml
    │   └── rbac.yaml
    ├── config/                       ← Frack's persona + framework config
    │   ├── SOUL.md
    │   ├── TOOLS.md
    │   └── openclaw.json
    ├── shared/                       ← Git submodule → l3ocifer/homelab
    ├── .github/workflows/
    │   ├── build.yml
    │   └── upstream-sync.yml
    ├── PATCHES.md
    ├── CHANGELOG.md
    └── README.md
```

## Deploying

ArgoCD's `frack` Application in
[`l3ocifer/homelab/argocd/apps/agents.yaml`](https://github.com/l3ocifer/homelab/blob/main/argocd/apps/agents.yaml)
points at this repo's `homelab/k8s` path. Push to `main` →
GitHub Actions builds + pushes
`ghcr.io/l3ocifer/frack-openclaw:latest` → ArgoCD Image Updater rolls
the Deployment.

## Building locally

```bash
git clone --recurse-submodules git@github.com:l3ocifer/frack-openclaw.git
cd frack-openclaw
docker build -f homelab/Dockerfile \
  -t ghcr.io/l3ocifer/frack-openclaw:latest .
```

## Frack's persona, in 30 seconds

The operator. Direct, terse, action-first. Owns the 12 businesses end-
to-end: customer comms, deploys, finance, social, support. Trusts
Frick to keep the cluster up; trusts Sancho to keep Leo's calendar
clean; trusts Vetinari to coordinate. See `config/SOUL.md`.

## Required env vars

Provided by `frack-secrets` SealedSecret in the cluster (sealed in
`l3ocifer/homelab/argocd/sealed-secrets/frack-secrets.yaml.template`).
See `homelab/config/openclaw.json` for the full list of what Frack
references.

## License

OpenClaw upstream: see [LICENSE](../LICENSE) at repo root.
Homelab additions in `homelab/`: same.
Persona text in `homelab/config/SOUL.md` is Leo Paska's IP.
