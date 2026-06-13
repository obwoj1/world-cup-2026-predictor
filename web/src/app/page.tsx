import { getFixtures, getPredictions, getTeamMap } from "@/lib/data";
import { MatchCard } from "@/components/MatchCard";

export default function FixturesPage() {
  const teams = getTeamMap();
  const fixtures = getFixtures();
  const preds = getPredictions();
  const predById = Object.fromEntries(preds.map((p) => [p.id, p]));

  const matchdays = [1, 2, 3];
  const byMatchday = matchdays.map((md) => ({
    md,
    fixtures: fixtures
      .filter((f) => f.stage === "group" && (f.matchday ?? f.matchweek) === md)
      .sort((a, b) => (a.group ?? "").localeCompare(b.group ?? "")),
  }));

  return (
    <div className="space-y-10">
      <section>
        <h1 className="text-3xl font-bold tracking-tight">Fixtures &amp; Predictions</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">
          Win / draw / loss probabilities and a most-likely scoreline for every group-stage
          match, each with expandable evidence-cited reasoning. Predictions come from an
          Elo-calibrated Poisson model. <strong className="text-slate-300">Not betting advice.</strong>
        </p>
      </section>

      {byMatchday.map(({ md, fixtures }) => (
        <section key={md}>
          <h2 className="mb-4 flex items-center gap-2 text-xl font-semibold">
            <span className="rounded-md bg-pitch-700/40 px-2 py-0.5 text-sm text-pitch-300">
              Matchday {md}
            </span>
            <span className="text-sm font-normal text-slate-500">{fixtures.length} matches</span>
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {fixtures.map((f) => {
              const pred = predById[f.id];
              if (!pred) return null;
              return (
                <div key={f.id} className="relative">
                  <span className="absolute -top-2 left-3 z-10 rounded bg-pitch-900 px-1.5 text-[10px] font-bold uppercase text-slate-400">
                    Group {f.group}
                  </span>
                  <MatchCard pred={pred} home={teams[f.home]} away={teams[f.away]} />
                </div>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
