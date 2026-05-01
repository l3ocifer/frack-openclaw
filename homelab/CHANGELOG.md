# Changelog

Frack-OpenClaw releases. Upstream OpenClaw versions tracked in
`homelab/PATCHES.md`.

## Unreleased

### Added

- Initial homelab/ overlay scaffolding
- Dockerfile builds OpenClaw from local source via pnpm + bun
  (mirrors upstream's build approach in a single-stage form)
- k8s manifests for `agents-shared` namespace, floating across the cluster
- config/{SOUL,TOOLS}.md + openclaw.json for the businesses-agent persona
- GitHub Actions: build.yml + upstream-sync.yml
- Submodule of l3ocifer/homelab at homelab/shared/ for shared docs

### Notes

- Frack's k8s manifests ship the floating + longhorn-backed
  configuration (no `nodeSelector`, longhorn-rwx graphs, longhorn-
  single state). Verified scaffolded structurally; build needs
  upstream's exact pnpm install/build sequence verified on first CI
  run.
