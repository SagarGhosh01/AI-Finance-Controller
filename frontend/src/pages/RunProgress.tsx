import React, { useEffect, useState } from 'react';
import { getRunProgress } from '../api/client';
import { ShieldCheck, CheckCircle2, Clock, Loader2, ArrowRight } from 'lucide-react';

interface RunProgressProps {
  runId: string;
  onComplete: () => void;
}

export const RunProgress: React.FC<RunProgressProps> = ({ runId, onComplete }) => {
  const [progress, setProgress] = useState<any>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      getRunProgress(runId)
        .then(data => {
          setProgress(data);
          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(interval);
          }
        })
        .catch(console.error);
    }, 500);

    return () => clearInterval(interval);
  }, [runId]);

  return (
    <div className="max-w-3xl mx-auto py-12 space-y-8">
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center mx-auto mb-4 text-blue-400">
          {progress?.status === 'completed' ? (
            <CheckCircle2 className="w-8 h-8 text-emerald-400" />
          ) : (
            <Loader2 className="w-8 h-8 animate-spin" />
          )}
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          {progress?.status === 'completed' ? 'Reconciliation Pipeline Complete' : 'Executing Autonomous Reconciliation'}
        </h1>
        <p className="text-sm font-mono text-slate-400 mt-1">Run ID: {runId}</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">STAGE PROGRESS</span>
            <span className="text-blue-400 font-bold uppercase">{progress?.status || 'RUNNING'}</span>
          </div>

          <div className="w-full bg-slate-950 rounded-full h-3 overflow-hidden border border-slate-800 p-0.5">
            <div
              className="bg-gradient-to-r from-blue-600 to-emerald-500 h-full rounded-full transition-all duration-500"
              style={{ width: progress?.status === 'completed' ? '100%' : '65%' }}
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-800 text-center font-mono">
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
            <div className="text-xs text-slate-400">Total Input Records</div>
            <div className="text-xl font-bold text-white mt-1">{progress?.total_records || 0}</div>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
            <div className="text-xs text-slate-400">Matched Records</div>
            <div className="text-xl font-bold text-emerald-400 mt-1">{progress?.matched_count || 0}</div>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
            <div className="text-xs text-slate-400">Exception Items</div>
            <div className="text-xl font-bold text-amber-400 mt-1">{progress?.exception_count || 0}</div>
          </div>
        </div>

        {progress?.status === 'completed' && (
          <div className="pt-4 text-center">
            <button
              onClick={onComplete}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow-lg shadow-emerald-600/30 transition-all text-sm"
            >
              <span>View Measured Reconciliation Results</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
