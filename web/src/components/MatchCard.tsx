"use client";

import { useState } from "react";
import type { Prediction, Team, MatchResult } from "@/lib/types";
import { confidenceColor, flag } from "@/lib/format";
import { ProbBar } from "./ProbBar";

export function MatchCard({
  pred,
  home,
  away,
  result,
  homeName: homeNameProp,
  awayName: awayNameProp,
  date,
  venue,
}: {
  pred?: Prediction;
  home?: Team;
  away?: Team;
  result?: MatchResult;
  homeName?: string;
  awayName?: string;
  date?: string | null;
  venue?: string | null;
}) {
  const [open, setOpen] = useState(false);
  const homeName = home?.name ?? homeNameProp ?? pred?.home ?? "TBD";
  const awayName = away?.name ?? awayNameProp ?? pred?.away ?? "TBD";

  const dateLabel = date
    ? new Date(`${date}T12:00:00Z`).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      })
    : null;

  // Center score: actual result (if played) else predicted scoreline.
  const centerScore = result
    ? `${result.home_goals}–${result.away_goals}`
    : pred
    ? `${pred.predicted_scoreline.home}–${pred.predicted_scoreline.away}`
    : "vs";

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-white/20">
      <div className="mb-2 flex items-center justify-between text-[10px] uppercase tracking-wide text-slate-500">
        <span>{dateLabel}</span>
        {result && (
          <span className="rounded bg-slate-500/15 px-1.5 py-0.5 font-semibold text-slate-300">
            Full time
          </span>
        )}
      </div>
      <div className="flex items-center justify-between gap-3">
        <div className="flex flex-1 items-center gap-2 text-sm font-semibold">
          <span className="text-lg">{flag(home?.elo_code)}</span>
          <span className="truncate">{homeName}</span>
        </div>
        <div className="shrink-0 px-2 text-center">
          <div className={`text-lg font-bold tabular-nums ${result ? "text-white" : ""}`}>
            {centerScore}
          </div>
          <div className="text-[10px] uppercase tracking-wide text-slate-500">
            {result ? "result" : pred ? "predicted" : ""}
          </div>
        </div>
        <div className="flex flex-1 items-center justify-end gap-2 text-sm font-semibold">
          <span className="truncate text-right">{awayName}</span>
          <span className="text-lg">{flag(away?.elo_code)}</span>
        </div>
      </div>

      {pred && !result && (
        <div className="mt-3">
          <ProbBar
            home={pred.probabilities.home_win}
            draw={pred.probabilities.draw}
            away={pred.probabilities.away_win}
          />
        </div>
      )}

      {venue && <p className="mt-2 text-[11px] text-slate-500">{venue}</p>}

      {pred && !result && (
      <div className="mt-3 flex items-center justify-between">
        <span
          className={`rounded-full px-2 py-0.5 text-[11px] font-medium ring-1 ${confidenceColor(
            pred.confidence
          )}`}
        >
          {pred.confidence} confidence
        </span>
        <button
          onClick={() => setOpen((o) => !o)}
          className="text-xs font-medium text-pitch-400 hover:underline"
        >
          {open ? "Hide reasoning ▲" : "Why? ▼"}
        </button>
      </div>
      )}

      {open && pred && (
        <div className="mt-3 space-y-3 border-t border-white/10 pt-3 text-sm">
          <p className="leading-relaxed text-slate-300">{pred.reasoning}</p>

          {pred.players_to_watch.length > 0 && (
            <div>
              <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
                Players to watch
              </h4>
              <ul className="space-y-1">
                {pred.players_to_watch.map((p) => (
                  <li key={p.player_id} className="text-slate-300">
                    <span className="font-medium text-pitch-400">{p.name}</span>{" "}
                    <span className="text-slate-400">
                      ({p.team}
                      {p.position ? `, ${p.position}` : ""})
                    </span>{" "}
                    — {p.evidence}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex flex-wrap gap-2 text-[11px] text-slate-500">
            <span className="font-semibold uppercase tracking-wide">Evidence:</span>
            {pred.evidence_refs.map((r) => (
              <code key={r} className="rounded bg-white/5 px-1.5 py-0.5">
                {r}
              </code>
            ))}
            <span>· model {pred.model_version}</span>
          </div>
        </div>
      )}
    </div>
  );
}
