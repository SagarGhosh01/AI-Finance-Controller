import React, { useEffect, useState } from 'react';
import { getCashPosition } from '../api/client';
import { CashPosition as CashPositionType } from '../types';
import { MetricCard } from '../components/MetricCard';
import { DollarSign, ShieldCheck, AlertOctagon, CheckCircle2, Lock } from 'lucide-react';

interface CashPositionProps {
  runId: string;
}

export const CashPositionPage: React.FC<CashPositionProps> = ({ runId }) => {
  const [data, setData] = useState<CashPositionType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCashPosition(runId)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [runId]);

  if (loading || !data) {
    return <div className="p-8 text-center text-slate-400 font-mono">Calculating net confirmed cash position...</div>;
  }

  const isNetPositive = data.confirmed_cash_position >= 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Confirmed Net Cash Position</h1>
        <p className="text-sm text-slate-400 mt-1">
          Audited net cash balance derived strictly from 100% verified & matched records.
        </p>
      </div>

      {/* Main Net Balance Hero Banner */}
      <div className="p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Confirmed Reconciled Net Position</span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className={`text-4xl font-extrabold font-mono tracking-tight ${isNetPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
              ${data.confirmed_cash_position.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </span>
            <span className="text-xs font-mono text-slate-400 uppercase">{data.currency}</span>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-2 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Verified against {data.total_matched_count} matched input records.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-500/30 max-w-md">
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs font-mono uppercase">
            <AlertOctagon className="w-4 h-4" />
            Excluded Pending Exceptions Warning
          </div>
          <p className="text-xs text-slate-300 mt-1 leading-relaxed">
            Exactly <span className="font-bold text-amber-400">{data.excluded_pending_exceptions_count} unresolved exception items</span> are currently EXCLUDED from this net total to prevent false inflation or premature revenue recognition.
          </p>
        </div>
      </div>

      {/* Metric Breakdown Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="Total Matched Records"
          value={data.total_matched_count}
          subtitle="Input items confirmed"
          icon={<CheckCircle2 className="w-4 h-4" />}
          badgeColor="emerald"
        />
        <MetricCard
          title="Confirmed Matches"
          value={data.matched_summary.matches_count}
          subtitle="Reconciled transaction pairs"
          icon={<Lock className="w-4 h-4" />}
          badgeColor="blue"
        />
        <MetricCard
          title="Pending Exceptions"
          value={data.excluded_pending_exceptions_count}
          subtitle="Unverified items held out"
          icon={<AlertOctagon className="w-4 h-4" />}
          badgeColor="amber"
        />
      </div>
    </div>
  );
};
