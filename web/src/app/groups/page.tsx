import { getTeams, getResults, getFixtures, getProjections } from "@/lib/data";
import { flag, pct } from "@/lib/format";
import type { Team } from "@/lib/types";

export default function GroupsPage() {
  const teams = getTeams();
  const results = getResults();
  const projections = getProjections();
  const fixtures = getFixtures();
  const projById = Object.fromEntries((projections?.teams ?? []).map((t) => [t.id, t]));

  // Actual standings from any played results.
  type Row = { played: number; pts: number; gd: number; gf: number };
  const standings: Record<string, Row> = Object.fromEntries(
    teams.map((t) => [t.id, { played: 0, pts: 0, gd: 0, gf: 0 }])
  );
  const fixtureById = Object.fromEntries(fixtures.map((f) => [f.id, f]));
  for (const r of results) {
    const fx = fixtureById[r.id];
    if (!fx) continue;
    const h = standings[fx.home];
    const a = standings[fx.away];
    if (!h || !a) continue;
    h.played++; a.played++;
    h.gf += r.home_goals; a.gf += r.away_goals;
    h.gd += r.home_goals - r.away_goals; a.gd += r.away_goals - r.home_goals;
    if (r.home_goals > r.away_goals) h.pts += 3;
    else if (r.away_goals > r.home_goals) a.pts += 3;
    else { h.pts += 1; a.pts += 1; }
  }
  const anyPlayed = results.length > 0;

  const groups = [...new Set(teams.map((t) => t.group))].sort();
  const byGroup: Record<string, Team[]> = {};
  for (const g of groups) {
    byGroup[g] = teams
      .filter((t) => t.group === g)
      .sort((a, b) =>
        anyPlayed
          ? standings[b.id].pts - standings[a.id].pts || standings[b.id].gd - standings[a.id].gd
          : (projById[b.id]?.p_advance_group ?? 0) - (projById[a.id]?.p_advance_group ?? 0)
      );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Group Tables</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">
          {anyPlayed
            ? "Live standings from played results, with each team's simulated probability of advancing."
            : "No matches played yet — teams are ordered by their simulated probability of advancing to the knockout stage."}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {groups.map((g) => (
          <div key={g} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
            <h2 className="mb-3 text-lg font-semibold">Group {g}</h2>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[11px] uppercase tracking-wide text-slate-500">
                  <th className="pb-2 font-medium">Team</th>
                  <th className="pb-2 text-center font-medium">Elo</th>
                  {anyPlayed && <th className="pb-2 text-center font-medium">Pts</th>}
                  <th className="pb-2 text-right font-medium">Advance</th>
                </tr>
              </thead>
              <tbody>
                {byGroup[g].map((t, i) => (
                  <tr key={t.id} className="border-t border-white/5">
                    <td className="py-1.5">
                      <span className={i < 2 ? "font-semibold" : "text-slate-300"}>
                        <span className="mr-1.5">{flag(t.elo_code)}</span>
                        {t.name}
                      </span>
                    </td>
                    <td className="text-center tabular-nums text-slate-400">{t.elo ?? "—"}</td>
                    {anyPlayed && (
                      <td className="text-center font-semibold tabular-nums">
                        {standings[t.id].pts}
                      </td>
                    )}
                    <td className="text-right tabular-nums">
                      {projById[t.id] ? (
                        <span className="text-pitch-300">{pct(projById[t.id].p_advance_group)}</span>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  );
}
