import { getProjections, getTeamMap } from "@/lib/data";
import { flag, pct } from "@/lib/format";

export default function BracketPage() {
  const projections = getProjections();
  const teams = getTeamMap();

  if (!projections) {
    return (
      <div>
        <h1 className="text-3xl font-bold">Title Race</h1>
        <p className="mt-3 text-slate-400">
          No simulation found. Run <code className="text-pitch-400">python simulate.py</code> in the
          pipeline to generate tournament odds.
        </p>
      </div>
    );
  }

  const rows = projections.teams;
  const cols: { key: keyof (typeof rows)[number]; label: string }[] = [
    { key: "p_advance_group", label: "R32" },
    { key: "p_reach_r16", label: "R16" },
    { key: "p_reach_qf", label: "QF" },
    { key: "p_reach_sf", label: "SF" },
    { key: "p_reach_final", label: "Final" },
    { key: "p_champion", label: "Champion" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Title Race</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">
          Tournament odds from a Monte Carlo simulation of{" "}
          <strong className="text-slate-300">{projections.sims.toLocaleString()}</strong> full
          tournaments — group stage through final, including the official Round-of-32 bracket.
          Each column is the probability of reaching that round.
        </p>
      </div>

      <div className="overflow-x-auto rounded-xl border border-white/10 bg-white/[0.03]">
        <table className="w-full min-w-[640px] text-sm">
          <thead>
            <tr className="border-b border-white/10 text-left text-[11px] uppercase tracking-wide text-slate-500">
              <th className="px-4 py-3 font-medium">#</th>
              <th className="px-4 py-3 font-medium">Team</th>
              <th className="px-2 py-3 text-center font-medium">Grp</th>
              {cols.map((c) => (
                <th key={c.key} className="px-3 py-3 text-right font-medium">
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((t, i) => (
              <tr key={t.id} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02]">
                <td className="px-4 py-2 tabular-nums text-slate-500">{i + 1}</td>
                <td className="px-4 py-2 font-medium">
                  <span className="mr-1.5">{flag(teams[t.id]?.elo_code)}</span>
                  {t.name}
                </td>
                <td className="px-2 py-2 text-center text-slate-400">{t.group}</td>
                {cols.map((c) => {
                  const v = t[c.key] as number;
                  const champ = c.key === "p_champion";
                  return (
                    <td
                      key={c.key}
                      className={`px-3 py-2 text-right tabular-nums ${
                        champ ? "font-semibold text-pitch-300" : "text-slate-300"
                      }`}
                    >
                      {v >= 0.001 ? pct(v, champ ? 1 : 0) : "—"}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-500">
        Model {projections.model_version} · {projections.method}. Probabilistic forecast, not betting advice.
      </p>
    </div>
  );
}
