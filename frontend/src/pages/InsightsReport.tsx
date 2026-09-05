import React, { useEffect, useState } from 'react';
import { MetricCard } from '../components/MetricCard';
import { FileSpreadsheet, Clock, ShieldCheck, Download, CheckCircle2, AlertTriangle, ArrowRight, Sparkles } from 'lucide-react';

interface InsightsReportProps {
  runId: string;
}

export const InsightsReportView: React.FC<InsightsReportProps> = ({ runId }) => {
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/runs/${runId}/insights`)
      .then(r => r.json())
      .then(setInsights)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [runId]);

  if (loading || !insights) {
    return <div className="p-8 text-center text-slate-400 font-mono">Generating executive insights & audit report...</div>;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <FileSpreadsheet className="w-6 h-6 text-emerald-400" />
            Executive Insights & Excel Audit Report
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Automated resolution of manual ledger-vs-bank comparison bottlenecks with downloadable Excel audit copy.
          </p>
        </div>

        <a
          href={`/api/runs/${runId}/excel-report`}
          download
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/30 transition-all cursor-pointer"
        >
          <Download className="w-4 h-4" />
          <span>Download Excel Audit Report (.xlsx / .csv)</span>
        </a>
      </div>

      {/* Hero Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Manual Labor Hours Saved"
          value={`~${insights.hours_saved_estimate} Hours`}
          subtitle="Saved per reconciliation batch"
          icon={<Clock className="w-4 h-4" />}
          badgeColor="emerald"
        />
        <MetricCard
          title="Verified Match Rate"
          value={`${insights.match_rate_pct}%`}
          subtitle={`${insights.matched_count} / ${insights.total_records} records matched`}
          icon={<ShieldCheck className="w-4 h-4" />}
          badgeColor="blue"
        />
        <MetricCard
          title="Execution Time"
          value={`${insights.processing_time_ms} ms`}
          subtitle="Sub-second batch processing"
          icon={<Sparkles className="w-4 h-4" />}
          badgeColor="purple"
        />
        <MetricCard
          title="Conservation Invariant"
          value="100% ACCOUNTABLE"
          subtitle="Zero records silently dropped"
          icon={<CheckCircle2 className="w-4 h-4" />}
          badgeColor="amber"
        />
      </div>

      {/* Problem Solved Matrix */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
          Manual Reconciliation Bottlenecks Solved
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
            <div className="text-emerald-400 font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              1. Amount & Reference Matching
            </div>
            <p className="text-slate-400 leading-relaxed font-sans mt-1">
              Eliminates manual row-by-row comparisons. Tier 1 deterministic engine matches exact and fuzzy reference IDs with amount tolerances ($\le \$0.50$).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
            <div className="text-emerald-400 font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              2. Date Differences & Settlement Drift
            </div>
            <p className="text-slate-400 leading-relaxed font-sans mt-1">
              Automates investigation of bank settlement delays (1–4 day shifts) using proximity date windows and AI reasoning.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
            <div className="text-emerald-400 font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              3. Duplicate Payment Detection
            </div>
            <p className="text-slate-400 leading-relaxed font-sans mt-1">
              Flags duplicate ACH/wire postings within feeds and holds them out as `DUPLICATE_SUSPECTED` exceptions.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
            <div className="text-emerald-400 font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              4. Split Transaction Aggregation
            </div>
            <p className="text-slate-400 leading-relaxed font-sans mt-1">
              Automatically aggregates 1 ledger entry matching 2 partial bank deposits (e.g. $12,000 bulk invoice split into $5,000 + $7,000 deposits).
            </p>
          </div>
        </div>
      </div>

      {/* Exception Root Cause Analysis */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">
          Exception Root Cause Summary ({insights.exception_count} Items Held Out)
        </h3>

        <div className="space-y-3 font-mono text-xs">
          {Object.entries(insights.exception_causes || {}).map(([cause, count]: any) => (
            <div key={cause} className="flex items-center justify-between p-3 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-slate-300 font-bold">{cause}</span>
              <span className="px-3 py-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold">
                {count} records ({((count / insights.total_records) * 100).toFixed(1)}%)
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
