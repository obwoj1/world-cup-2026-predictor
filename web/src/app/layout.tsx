import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "World Cup 2026 — Predictions & Analysis",
  description:
    "Probabilistic, evidence-cited forecasts for every FIFA World Cup 2026 match. Not betting advice.",
};

const NAV = [
  { href: "/", label: "Fixtures" },
  { href: "/groups", label: "Groups" },
  { href: "/bracket", label: "Title Race" },
  { href: "/players", label: "Players" },
  { href: "/reconciliations", label: "Reconciliation" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="sticky top-0 z-20 border-b border-white/10 bg-pitch-900/80 backdrop-blur">
          <nav className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3">
            <Link href="/" className="mr-2 text-lg font-bold tracking-tight">
              ⚽ WC&nbsp;2026 <span className="text-pitch-400">Predictor</span>
            </Link>
            {NAV.map((n) => (
              <Link
                key={n.href}
                href={n.href}
                className="text-sm font-medium text-slate-300 transition hover:text-pitch-400"
              >
                {n.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
        <footer className="mx-auto max-w-6xl px-4 py-10 text-xs text-slate-500">
          <p>
            Probabilistic forecasting &amp; analysis tool — <strong>not betting advice</strong>.
            Predictions are model estimates with explicit uncertainty. Data:
            eloratings.net and others (see repo <code>data/sources/</code>). Not affiliated with FIFA.
          </p>
        </footer>
      </body>
    </html>
  );
}
