// Copies the pipeline's JSON outputs (repo-root /data) into web/data so the Next app
// can read them locally and on Vercel without a second source of truth in git.
// Runs automatically before `dev` and `build`.
import { cpSync, mkdirSync, existsSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SRC = join(__dirname, "..", "..", "data");
const DEST = join(__dirname, "..", "data");

const FILES = [
  "teams.json",
  "fixtures.json",
  "results.json",
  "predictions.json",
  "projections.json",
  "players.json",
];

if (!existsSync(SRC)) {
  console.warn(`[sync-data] source ${SRC} not found — skipping (using existing web/data)`);
  process.exit(0);
}

mkdirSync(DEST, { recursive: true });
let copied = 0;
for (const f of FILES) {
  const from = join(SRC, f);
  if (existsSync(from)) {
    cpSync(from, join(DEST, f));
    copied++;
  }
}

// Also sync reconciliation markdown logs if present.
const reconSrc = join(__dirname, "..", "..", "reconciliations");
const reconDest = join(DEST, "reconciliations");
if (existsSync(reconSrc)) {
  mkdirSync(reconDest, { recursive: true });
  for (const f of readdirSync(reconSrc)) {
    if (f.endsWith(".md")) cpSync(join(reconSrc, f), join(reconDest, f));
  }
}

console.log(`[sync-data] copied ${copied} data files -> web/data`);
