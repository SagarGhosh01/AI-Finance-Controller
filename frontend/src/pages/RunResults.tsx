import React, { useEffect, useState } from 'react';
import { getRunReport, approveClose } from '../api/client';
import { RunReport } from '../types';
import { MetricCard } from '../components/MetricCard';
import { IntegrityBanner } from '../components/IntegrityBanner';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { ShieldCheck, Clock, Cpu, CheckCircle2, Download, AlertTriangle, ArrowRight } from 'lucide-react';

interface RunResultsProps {
  runId: string;
  onNavigateToExceptions: () => void;
  onNavigateToCashPosition: () => void;
}

export const RunResults: React.FC<RunResultsProps> = ({
  runId,
  onNavigateToExceptions,
  onNavigateToCashPosition,
}) => {
  const [report, setReport] = useState<RunReport | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchReport = () => {
    getRunReport(runId)
      .then(setReport)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchReport();
  }, [runId]);

  const handleApprove = async () => {
    try {
      await approveClose(runId);
      fetchReport();
    } catch (e: any) {
      alert('Approval failed: ' + e.message);
    }
  };

  if (loading || !report) {
    return <div className="p-8 text-center text-slate-400 font-mono">Loading reconciliation results...</div>;
  }

  const { run, breakdown_by_tier, breakdown_by_exception_type, integrity_check_passed } = report;

  const tierChartData = Object.entries(breakdown_by_tier).map(([name, value]) => ({
    name: name.toUpperCase(),
    value,
  }));

  const COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ec4899'];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-white tracking-tight">Reconciliation Run Audit Report</h1>
            <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-bold uppercase ${
              run.approved_by
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
            }`}>
              {run.approved_by ? 'CLOSE APPROVED' : run.status}
            </span>
          </div>
          <p className="text-xs font-mono text-slate-400 mt-1">Run ID: {run.id}</p>
        </div>

        <div className="flex items-center gap-2">
          <a
            href={`/api/runs/${run.id}/report?format=csv`}
            download
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV Audit</span>
          </a>

          {!run.approved_by && (
            <button
              onClick={handleApprove}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/30 transition-all"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Approve Period Close</span>
            </button>
          )}
        </div>
      </div>

      {/* Conservation Invariant Banner */}
      <IntegrityBanner
        matchedCount={run.matched_count}
        exceptionCount={run.exception_count}
        totalRecords={run.total_records}
      />

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Measured Match Rate"
          value={`${run.match_rate_pct}%`}
          subtitle={`${run.matched_count} / ${run.total_records} input records matched`}
          icon={<ShieldCheck className="w-4 h-4" />}
          badgeColor="emerald"
        />
        <MetricCard
          title="Unresolved Exceptions"
          value={run.exception_count}
          subtitle="Honest exception set"
          icon={<AlertTriangle className="w-4 h-4" />}
          badgeColor="amber"
        />
        <MetricCard
          title="Processing Throughput"
          value={`${run.processing_time_ms} ms`}
          subtitle={`Speed: ${((run.total_records / (run.processing_time_ms / 1000)) || 0).toFixed(0)} records/sec`}
          icon={<Clock className="w-4 h-4" />}
          badgeColor="blue"
        />
        <MetricCard
          title="LLM Cost Transparency"
          value={`${run.llm_calls_made} calls`}
          subtitle={`${run.llm_tokens_used} tokens consumed`}
          icon={<Cpu className="w-4 h-4" />}
          badgeColor="purple"
        />
      </div>

      {/* Breakdown Charts & Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Match Tier Breakdown */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">
            Match Distribution by Engine Tier
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={tierChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {tierChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Exception Breakdown List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
              Exception Classification Breakdown
            </h3>
            <button
              onClick={onNavigateToExceptions}
              className="text-xs text-amber-400 hover:text-amber-300 font-medium flex items-center gap-1"
            >
              <span>Review Exceptions</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {Object.entries(breakdown_by_exception_type).map(([type, count]) => (
              <div
                key={type}
                className="flex items-center justify-between p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 font-mono text-xs"
              >
                <span className="text-slate-300 font-medium">{type}</span>
                <span className="px-2.5 py-1 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold">
                  {count} items
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Navigation Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          onClick={onNavigateToExceptions}
          className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-500/40 cursor-pointer transition-all flex items-center justify-between group"
        >
          <div>
            <h4 className="font-semibold text-sm text-slate-200 group-hover:text-amber-400 transition-colors">
              Human-in-the-Loop Exception Review ({run.exception_count} items)
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Inspect agent reasoning, accept suggested matches, or manually resolve mismatches.
            </p>
          </div>
          <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-amber-400 transition-colors" />
        </div>

        <div
          onClick={onNavigateToCashPosition}
          className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-emerald-500/40 cursor-pointer transition-all flex items-center justify-between group"
        >
          <div>
            <h4 className="font-semibold text-sm text-slate-200 group-hover:text-emerald-400 transition-colors">
              Confirmed Net Cash Position
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              View confirmed net cash position calculated exclusively from verified matched records.
            </p>
          </div>
          <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-emerald-400 transition-colors" />
        </div>
      </div>
    </div>
  );
};
