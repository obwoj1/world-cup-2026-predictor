import { pct } from "@/lib/format";

export function ProbBar({
  home,
  draw,
  away,
}: {
  home: number;
  draw: number;
  away: number;
}) {
  return (
    <div>
      <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-white/5">
        <div className="bg-pitch-500" style={{ width: pct(home) }} title={`Home ${pct(home)}`} />
        <div className="bg-slate-400" style={{ width: pct(draw) }} title={`Draw ${pct(draw)}`} />
        <div className="bg-sky-500" style={{ width: pct(away) }} title={`Away ${pct(away)}`} />
      </div>
      <div className="mt-1 flex justify-between text-[11px] text-slate-400">
        <span className="text-pitch-400">{pct(home)}</span>
        <span>draw {pct(draw)}</span>
        <span className="text-sky-400">{pct(away)}</span>
      </div>
    </div>
  );
}
