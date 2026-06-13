import { getPredictions, getTeamMap } from "@/lib/data";
import { flag } from "@/lib/format";

export default function PlayersPage() {
  const preds = getPredictions();
  const teams = getTeamMap();

  // Aggregate every "player to watch" mention across predictions.
  const counts: Record<string, { name: string; team: string; evidence: string; mentions: number }> = {};
  for (const p of preds) {
    for (const ptw of p.players_to_watch) {
      const cur = counts[ptw.player_id] ?? {
        name: ptw.name,
        team: ptw.team,
        evidence: ptw.evidence,
        mentions: 0,
      };
      cur.mentions++;
      counts[ptw.player_id] = cur;
    }
  }
  const players = Object.values(counts).sort((a, b) => b.mentions - a.mentions);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Players to Watch</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">
          Standout players flagged across upcoming matches, ranked by how often they appear in a
          prediction&apos;s &ldquo;players to watch&rdquo; list.
        </p>
      </div>

      {players.length === 0 ? (
        <div className="rounded-xl border border-dashed border-white/15 bg-white/[0.02] p-8 text-center">
          <p className="text-slate-300">Player data not populated yet.</p>
          <p className="mt-2 text-sm text-slate-500">
            The squad/player dataset (<code>data/players.json</code>) is built in the next data pass.
            Once it lands, each prediction will cite 1–3 players with stats-backed evidence and they
            will rank here automatically.
          </p>
        </div>
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2">
          {players.map((p) => (
            <li key={p.name} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-center justify-between">
                <span className="font-semibold">
                  <span className="mr-1.5">{flag(teams[p.team]?.elo_code)}</span>
                  {p.name}
                </span>
                <span className="rounded-full bg-pitch-700/40 px-2 py-0.5 text-xs text-pitch-300">
                  {p.mentions}× flagged
                </span>
              </div>
              <p className="mt-2 text-sm text-slate-400">{p.evidence}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
