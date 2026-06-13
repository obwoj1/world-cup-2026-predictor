export interface Team {
  id: string;
  name: string;
  elo_code: string;
  confederation: string;
  group: string;
  elo: number | null;
  elo_rank: number | null;
  fifa_rank: number | null;
  form: unknown | null;
  xg: unknown | null;
  wc_knockout_history: string | null;
  sources: string[];
}

export interface Fixture {
  id: string;
  matchweek: number;
  stage: string;
  group: string | null;
  matchday?: number;
  date: string | null;
  venue: string | null;
  home: string;
  away: string;
}

export interface MatchResult {
  id: string;
  home_goals: number;
  away_goals: number;
  status: string;
}

export interface PlayerToWatch {
  player_id: string;
  name: string;
  team: string;
  evidence: string;
}

export interface Prediction {
  id: string;
  generated_at: string;
  model_version: string;
  stage: string;
  group: string | null;
  home: string;
  away: string;
  probabilities: { home_win: number; draw: number; away_win: number };
  predicted_scoreline: { home: number; away: number };
  expected_goals: { home: number; away: number };
  confidence: "low" | "medium" | "high";
  reasoning: string;
  players_to_watch: PlayerToWatch[];
  evidence_refs: string[];
}

export interface TeamProjection {
  id: string;
  name: string;
  group: string;
  elo: number;
  p_advance_group: number;
  p_reach_r16: number;
  p_reach_qf: number;
  p_reach_sf: number;
  p_reach_final: number;
  p_champion: number;
}

export interface Projections {
  generated_at: string;
  model_version: string;
  sims: number;
  method: string;
  teams: TeamProjection[];
}
