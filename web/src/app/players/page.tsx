import { getPlayers, getTeamMap } from "@/lib/data";
import { flag } from "@/lib/format";
import type { Player } from "@/lib/types";

const ROLE_LABEL: Record<string, string> = {
  attack: "Attack",
  midfield: "Midfield",
  defence: "Defence",
};

export default function PlayersPage() {
  const players = getPlayers();
  const teams = getTeamMap();

  if (players.length === 0) {
    return (
      <div>
        <h1 className="text-3xl font-bold">Players to Watch</h1>
        <p className="mt-3 text-slate-400">
          Player data not populated. Run <code className="text-pitch-400">python build_players.py</code>.
        </p>
      </div>
    );
  }

  const keyPlayers = players
    .filter((p) => p.key)
    .sort((a, b) => (b.intl_goals ?? 0) - (a.intl_goals ?? 0));

  // group full squads by team
  const byTeam = new Map<string, Player[]>();
  for (const p of players) {
    if (!byTeam.has(p.team)) byTeam.set(p.team, []);
    byTeam.get(p.team)!.push(p);
  }
  const posOrder: Record<string, number> = { GK: 0, DF: 1, MF: 2, FW: 3 };
  const teamIds = [...byTeam.keys()].sort((a, b) =>
    (teams[a]?.name ?? a).localeCompare(teams[b]?.name ?? b)
  );

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Players</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">
          Full 26-man squads for all 48 teams ({players.length} players), with difference-makers
          across attack, midfield and defence flagged as <span className="text-pitch-400">key</span>.
          These power the &ldquo;players to watch&rdquo; on each match.
        </p>
      </div>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Key players to watch</h2>
        <ul className="grid gap-3 sm:grid-cols-2">
          {keyPlayers.slice(0, 24).map((p) => (
            <li key={p.id} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold">
                  <span className="mr-1.5">{flag(teams[p.team]?.elo_code)}</span>
                  {p.name}
                </span>
                <span className="shrink-0 rounded-full bg-pitch-700/40 px-2 py-0.5 text-xs text-pitch-300">
                  {ROLE_LABEL[p.key_role ?? ""] ?? p.position}
                </span>
              </div>
              <p className="mt-2 text-sm text-slate-400">{p.evidence}</p>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Full squads</h2>
        <div className="space-y-3">
          {teamIds.map((tid) => {
            const squad = byTeam
              .get(tid)!
              .slice()
              .sort(
                (a, b) =>
                  (posOrder[a.position] ?? 9) - (posOrder[b.position] ?? 9) ||
                  (b.intl_goals ?? 0) - (a.intl_goals ?? 0)
              );
            return (
              <details key={tid} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                <summary className="cursor-pointer font-semibold">
                  <span className="mr-1.5">{flag(teams[tid]?.elo_code)}</span>
                  {teams[tid]?.name ?? tid}
                  <span className="ml-2 text-xs font-normal text-slate-500">
                    {squad.length} players
                  </span>
                </summary>
                <table className="mt-3 w-full text-sm">
                  <thead>
                    <tr className="text-left text-[11px] uppercase tracking-wide text-slate-500">
                      <th className="py-1 font-medium">Pos</th>
                      <th className="py-1 font-medium">Player</th>
                      <th className="py-1 font-medium">Club</th>
                      <th className="py-1 text-center font-medium">Caps</th>
                      <th className="py-1 text-center font-medium">Gls</th>
                    </tr>
                  </thead>
                  <tbody>
                    {squad.map((p) => (
                      <tr key={p.id} className="border-t border-white/5">
                        <td className="py-1 text-slate-400">{p.position}</td>
                        <td className="py-1">
                          {p.name}
                          {p.key && (
                            <span className="ml-1.5 rounded bg-pitch-700/40 px-1 text-[10px] text-pitch-300">
                              key
                            </span>
                          )}
                        </td>
                        <td className="py-1 text-slate-400">{p.club ?? "—"}</td>
                        <td className="py-1 text-center tabular-nums text-slate-400">{p.caps ?? "—"}</td>
                        <td className="py-1 text-center tabular-nums text-slate-400">{p.intl_goals ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </details>
            );
          })}
        </div>
      </section>
    </div>
  );
}
