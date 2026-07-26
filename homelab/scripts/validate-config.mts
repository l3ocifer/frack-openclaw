/**
 * Validate homelab/config/openclaw.json against the schema in THIS checkout.
 *
 * Homelab-local, additive-only (see homelab/PATCHES.md, patch id
 * `homelab-config-validator`). Nothing upstream imports it, so it never
 * conflicts on a sync.
 *
 * Why this exists: the gateway validates its config with a *strict* zod schema
 * and exits non-zero when a key is unknown, so a config key that upstream
 * renames or retires turns into a CrashLoopBackOff that is only discovered
 * after the image builds and rolls. That is exactly how 2026-07-26 went —
 * `agents.defaults.compaction.reserveTokens` / `reserveTokensFloor` were
 * retired and `agents.defaults.memorySearch` moved to root `memory.search`,
 * and puck crash-looped 7 times before anyone read the logs.
 *
 * Run this after every `git merge upstream/main` and BEFORE pushing, so the
 * schema drift is caught against the merged source tree rather than in-cluster:
 *
 *   ./node_modules/.bin/tsx homelab/scripts/validate-config.mts
 *
 * Exit codes: 0 = valid, 1 = invalid (issues listed), 2 = usage/parse error.
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import JSON5 from "json5";
import { OpenClawSchema } from "../../src/config/zod-schema.js";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const target = process.argv[2] ?? resolve(repoRoot, "homelab/config/openclaw.json");

let parsed: unknown;
try {
  // The file is JSON5: it is heavily commented, and the comments carry the
  // provenance of every non-default key. The gateway reads it as JSON5 too.
  parsed = JSON5.parse(readFileSync(target, "utf8"));
} catch (err) {
  console.error(`FAIL ${target}\n  could not parse: ${(err as Error).message}`);
  process.exit(2);
}

const result = OpenClawSchema.safeParse(parsed);
if (result.success) {
  console.log(`OK   ${target}`);
  process.exit(0);
}

console.error(`FAIL ${target}`);
for (const issue of result.error.issues) {
  console.error(`  ${issue.path.join(".") || "<root>"}: ${issue.message}`);
}
console.error(
  "\nA renamed or retired key is the usual cause after an upstream sync.\n" +
    "Check src/commands/doctor/shared/legacy-config-migrations.* for where the\n" +
    "key moved, and the strict zod schema in src/config/zod-schema.*.ts for the\n" +
    "shape that replaced it.",
);
process.exit(1);
