import React from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';

interface IntegrityBannerProps {
  matchedCount: number;
  exceptionCount: number;
  totalRecords: number;
}

export const IntegrityBanner: React.FC<IntegrityBannerProps> = ({ matchedCount, exceptionCount, totalRecords }) => {
  const isPassed = matchedCount + exceptionCount === totalRecords;

  return (
    <div className={`p-4 rounded-xl border flex items-center justify-between transition-all ${
      isPassed
        ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
        : 'bg-rose-950/40 border-rose-500/30 text-rose-300'
    }`}>
      <div className="flex items-center gap-3">
        {isPassed ? (
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>
        ) : (
          <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20">
            <AlertTriangle className="w-5 h-5 text-rose-400" />
          </div>
        )}
        <div>
          <h4 className="font-semibold text-sm tracking-wide">
            {isPassed ? 'CONSERVATION INVARIANT PASSED' : 'INVARIANT VIOLATION DETECTED'}
          </h4>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Formula: Matched Records ({matchedCount}) + Exceptions ({exceptionCount}) = Total Input Records ({totalRecords})
          </p>
        </div>
      </div>
      <div className="text-right font-mono text-xs px-3 py-1.5 rounded-md bg-slate-900/60 border border-slate-800">
        Status: <span className={isPassed ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>{isPassed ? '100% ACCOUNTABLE' : 'UNACCOUNTED RECORDS'}</span>
      </div>
    </div>
  );
};
