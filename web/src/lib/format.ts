export const pct = (x: number, digits = 0): string => `${(x * 100).toFixed(digits)}%`;

export const confidenceColor = (c: string): string =>
  ({
    high: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
    medium: "bg-amber-500/15 text-amber-300 ring-amber-500/30",
    low: "bg-rose-500/15 text-rose-300 ring-rose-500/30",
  }[c] ?? "bg-slate-500/15 text-slate-300 ring-slate-500/30");

// Override map for eloratings codes that aren't ISO-3166 alpha-2 regional indicators.
const FLAG_OVERRIDE: Record<string, string> = {
  EN: "🏴󠁧󠁢󠁥󠁮󠁧󠁿", // England
  SQ: "🏴󠁧󠁢󠁳󠁣󠁴󠁿", // Scotland
  WA: "🏴󠁧󠁢󠁷󠁬󠁳󠁿", // Wales
};

/** Best-effort flag emoji from a 2-letter eloratings/ISO code. */
export function flag(code: string | undefined): string {
  if (!code) return "🏳️";
  if (FLAG_OVERRIDE[code]) return FLAG_OVERRIDE[code];
  if (code.length !== 2 || !/^[A-Za-z]{2}$/.test(code)) return "🏳️";
  const A = 0x1f1e6;
  const cc = code.toUpperCase();
  return String.fromCodePoint(A + cc.charCodeAt(0) - 65, A + cc.charCodeAt(1) - 65);
}
