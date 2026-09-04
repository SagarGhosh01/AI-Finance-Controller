import React, { useEffect, useState } from 'react';
import { listRuns } from '../api/client';
import { Run } from '../types';
import { MetricCard } from '../components/MetricCard';
import { PlayCircle, ShieldCheck, Activity, Clock, CheckCircle2, ArrowRight } from 'lucide-react';

interface DashboardProps {
  onSelectRun: (runId: string) => void;
  onNewRun: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onSelectRun, onNewRun }) => {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listRuns()
      .then(setRuns)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const totalProcessed = runs.reduce((acc, r) => acc + r.total_records, 0);
  const avgMatchRate = runs.length
    ? (runs.reduce((acc, r) => acc + r.match_rate_pct, 0) / runs.length).toFixed(1)
    : '0.0';
  const totalApproved = runs.filter(r => r.approved_by).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Reconciliation Operations Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">
            Autonomous multi-source verification engine & batch audit ledger.
          </p>
        </div>
        <button
          onClick={onNewRun}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium shadow-lg shadow-blue-600/30 transition-all text-sm"
        >
          <PlayCircle className="w-4 h-4" />
          <span>Launch Reconciliation Batch</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Runs"
          value={runs.length}
          subtitle="Batch runs logged"
          icon={<Activity className="w-4 h-4" />}
          badgeColor="blue"
        />
        <MetricCard
          title="Avg Match Rate"
          value={`${avgMatchRate}%`}
          subtitle="Measured verification accuracy"
          icon={<ShieldCheck className="w-4 h-4" />}
          badgeColor="emerald"
        />
        <MetricCard
          title="Total Input Records"
          value={totalProcessed}
          subtitle="Ledger & Bank items processed"
          icon={<Clock className="w-4 h-4" />}
          badgeColor="purple"
        />
        <MetricCard
          title="Period Close Approved"
          value={`${totalApproved} / ${runs.length}`}
          subtitle="Controller sign-offs"
          icon={<CheckCircle2 className="w-4 h-4" />}
          badgeColor="amber"
        />
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="font-semibold text-sm text-slate-200 uppercase tracking-wider">Historical Batch Runs</h2>
          <span className="text-xs font-mono text-slate-400">Total: {runs.length} runs</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 font-mono text-sm">Loading historical runs...</div>
        ) : runs.length === 0 ? (
          <div className="p-12 text-center">
            <ShieldCheck className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-300">No reconciliation runs executed yet</h3>
            <p className="text-xs text-slate-500 mt-1 mb-4">
              Start your first autonomous reconciliation over the 50+ record synthetic dataset.
            </p>
            <button
              onClick={onNewRun}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium"
            >
              <PlayCircle className="w-4 h-4" />
              <span>Launch First Run</span>
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/60 text-xs font-mono uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3">Run ID</th>
                  <th className="px-6 py-3">Date</th>
                  <th className="px-6 py-3">Sources</th>
                  <th className="px-6 py-3 text-right">Records</th>
                  <th className="px-6 py-3 text-right">Match Rate</th>
                  <th className="px-6 py-3 text-right">Exceptions</th>
                  <th className="px-6 py-3 text-right">Time</th>
                  <th className="px-6 py-3 text-center">Status</th>
                  <th className="px-6 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {runs.map(run => (
                  <tr key={run.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-mono text-xs text-blue-400 font-medium">
                      {run.id.substring(0, 8)}...
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {new Date(run.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-xs font-medium text-slate-300">
                      {run.source_a_name} vs {run.source_b_name}
                    </td>
                    <td className="px-6 py-4 text-xs font-mono text-right font-semibold">
                      {run.total_records}
                    </td>
                    <td className="px-6 py-4 text-xs font-mono text-right text-emerald-400 font-bold">
                      {run.match_rate_pct}%
                    </td>
                    <td className="px-6 py-4 text-xs font-mono text-right text-amber-400">
                      {run.exception_count}
                    </td>
                    <td className="px-6 py-4 text-xs font-mono text-right text-slate-400">
                      {run.processing_time_ms} ms
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-block px-2.5 py-1 rounded-full text-[11px] font-mono uppercase font-semibold ${
                        run.approved_by
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                      }`}>
                        {run.approved_by ? 'Approved' : run.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => onSelectRun(run.id)}
                        className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 font-medium"
                      >
                        <span>View</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
