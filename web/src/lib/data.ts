import { readFileSync, existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import type {
  Team,
  Fixture,
  MatchResult,
  Prediction,
  Projections,
  Player,
} from "./types";

// web/data is populated by scripts/sync-data.mjs (predev / prebuild).
const DATA_DIR = join(process.cwd(), "data");

function read<T>(file: string, fallback: T): T {
  const path = join(DATA_DIR, file);
  if (!existsSync(path)) return fallback;
  return JSON.parse(readFileSync(path, "utf-8")) as T;
}

export const getTeams = (): Team[] => read<Team[]>("teams.json", []);
export const getFixtures = (): Fixture[] => read<Fixture[]>("fixtures.json", []);
export const getResults = (): MatchResult[] => read<MatchResult[]>("results.json", []);
export const getPredictions = (): Prediction[] => read<Prediction[]>("predictions.json", []);
export const getPlayers = (): Player[] => read<Player[]>("players.json", []);
export const getProjections = (): Projections | null =>
  read<Projections | null>("projections.json", null);

export function getTeamMap(): Record<string, Team> {
  return Object.fromEntries(getTeams().map((t) => [t.id, t]));
}

export interface ReconLog {
  slug: string;
  title: string;
  body: string;
}

export function getReconciliations(): ReconLog[] {
  const dir = join(DATA_DIR, "reconciliations");
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith(".md") && f !== "README.md")
    .sort()
    .map((f) => {
      const body = readFileSync(join(dir, f), "utf-8");
      const titleMatch = body.match(/^#\s+(.+)$/m);
      return {
        slug: f.replace(/\.md$/, ""),
        title: titleMatch ? titleMatch[1] : f,
        body,
      };
    });
}
