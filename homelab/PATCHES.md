# Local patches vs upstream openclaw/openclaw

Track non-additive changes (anything outside `homelab/`). Additive
changes — files added under `homelab/` — don't need entries.

## Active patches

_(none today — Frack ships pure-vanilla OpenClaw, customized only via
configs in `homelab/config/`)_

## Resolving an upstream merge conflict

When `git merge upstream/main` reports a conflict in a file we patch:

1. Identify the patch from the list below
2. Re-apply it to the merged result
3. Bump `Last applied` for that patch
4. Commit with message `merge: upstream <sha> + reapply <patch-id>`
