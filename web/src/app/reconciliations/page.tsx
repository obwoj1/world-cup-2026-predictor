import { getReconciliations } from "@/lib/data";

export default function ReconciliationsPage() {
  const logs = getReconciliations();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Reconciliation Log</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">
          After each matchweek the model is checked against actual results: upsets are explained,
          ratings/form are updated, and predictions for remaining matches are re-run. Each entry
          records what changed and why.
        </p>
      </div>

      {logs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-white/15 bg-white/[0.02] p-8 text-center">
          <p className="text-slate-300">No reconciliations yet.</p>
          <p className="mt-2 text-sm text-slate-500">
            The first log appears after Matchweek 1 results come in. Run{" "}
            <code className="text-pitch-400">python reconcile.py --matchweek 1</code> to generate it.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {logs.map((log) => (
            <details
              key={log.slug}
              className="rounded-xl border border-white/10 bg-white/[0.03] p-4"
            >
              <summary className="cursor-pointer text-lg font-semibold">{log.title}</summary>
              <pre className="mt-3 overflow-x-auto whitespace-pre-wrap border-t border-white/10 pt-3 text-sm leading-relaxed text-slate-300">
                {log.body}
              </pre>
            </details>
          ))}
        </div>
      )}
    </div>
  );
}
