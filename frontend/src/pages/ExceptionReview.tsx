import React, { useEffect, useState } from 'react';
import { getRunExceptions, resolveException } from '../api/client';
import { ExceptionItem } from '../types';
import { ShieldCheck, Filter, Check, X, Flag, HelpCircle, ChevronRight, CornerDownRight } from 'lucide-react';

interface ExceptionReviewProps {
  runId: string;
}

export const ExceptionReview: React.FC<ExceptionReviewProps> = ({ runId }) => {
  const [exceptions, setExceptions] = useState<ExceptionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('ALL');
  const [selectedEx, setSelectedEx] = useState<ExceptionItem | null>(null);
  const [notes, setNotes] = useState('');

  const fetchExceptions = () => {
    getRunExceptions(runId, filterType === 'ALL' ? undefined : filterType)
      .then(setExceptions)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchExceptions();
  }, [runId, filterType]);

  const handleAction = async (action: 'accept' | 'reject' | 'manual' | 'flag') => {
    if (!selectedEx) return;
    try {
      const updated = await resolveException(selectedEx.id, action, notes);
      setSelectedEx(updated);
      fetchExceptions();
      setNotes('');
    } catch (e: any) {
      alert('Action failed: ' + e.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Human-in-the-Loop Exception Workbench</h1>
          <p className="text-sm text-slate-400 mt-1">
            Review agent-classified exceptions, inspect reasoning, and resolve edge cases.
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterType}
            onChange={e => setFilterType(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-xs font-mono text-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Exception Types</option>
            <option value="UNMATCHED_LEDGER">UNMATCHED_LEDGER</option>
            <option value="UNMATCHED_BANK">UNMATCHED_BANK</option>
            <option value="AMOUNT_MISMATCH">AMOUNT_MISMATCH</option>
            <option value="DATE_MISMATCH">DATE_MISMATCH</option>
            <option value="DUPLICATE_SUSPECTED">DUPLICATE_SUSPECTED</option>
            <option value="NEEDS_HUMAN_REVIEW">NEEDS_HUMAN_REVIEW</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Exceptions List */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
            <h2 className="font-semibold text-sm text-slate-200 uppercase tracking-wider">Unresolved Exception Items</h2>
            <span className="text-xs font-mono text-slate-400">{exceptions.length} items</span>
          </div>

          {loading ? (
            <div className="p-8 text-center text-slate-500 font-mono text-sm">Loading exception list...</div>
          ) : exceptions.length === 0 ? (
            <div className="p-12 text-center text-slate-500 font-mono text-xs">
              No exceptions found matching current filter.
            </div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {exceptions.map(ex => (
                <div
                  key={ex.id}
                  onClick={() => setSelectedEx(ex)}
                  className={`p-4 hover:bg-slate-800/50 cursor-pointer transition-colors ${
                    selectedEx?.id === ex.id ? 'bg-slate-800/80 border-l-4 border-blue-500' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-white">{ex.record_code}</span>
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                        Src: {ex.source === 'A' ? 'Ledger' : 'Bank'}
                      </span>
                    </div>

                    <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded font-semibold ${
                      ex.resolution_status === 'open'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}>
                      {ex.resolution_status}
                    </span>
                  </div>

                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-xs font-mono font-semibold text-amber-400">{ex.exception_type}</span>
                    {ex.candidate_record_code && (
                      <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                        <CornerDownRight className="w-3 h-3 text-slate-500" />
                        Candidate: {ex.candidate_record_code}
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-slate-400 mt-1 line-clamp-1">{ex.reasoning}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Detail & Action Drawer */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-fit sticky top-20">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4 border-b border-slate-800 pb-3">
            Agent Reasoning & Human Actions
          </h3>

          {selectedEx ? (
            <div className="space-y-4">
              <div className="space-y-1 font-mono text-xs">
                <div className="text-slate-400">TARGET RECORD:</div>
                <div className="text-sm font-bold text-white">{selectedEx.record_code}</div>
              </div>

              <div className="space-y-1 font-mono text-xs">
                <div className="text-slate-400">EXCEPTION TYPE:</div>
                <div className="text-xs font-bold text-amber-400">{selectedEx.exception_type}</div>
              </div>

              {selectedEx.candidate_record_code && (
                <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1">
                  <div className="text-[11px] font-mono text-slate-400">PROXIMITY CANDIDATE:</div>
                  <div className="text-xs font-mono font-bold text-blue-400">{selectedEx.candidate_record_code}</div>
                </div>
              )}

              <div className="space-y-1">
                <div className="text-xs font-mono text-slate-400">AGENT REASONING:</div>
                <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 font-mono leading-relaxed">
                  {selectedEx.reasoning}
                </div>
              </div>

              <div className="space-y-2 pt-2">
                <label className="block text-xs font-mono text-slate-400">Resolution Notes</label>
                <textarea
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  placeholder="Optional analyst notes..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs font-mono text-white focus:outline-none focus:border-blue-500 h-20"
                />
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2">
                <button
                  onClick={() => handleAction('accept')}
                  className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md transition-all"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Accept Match</span>
                </button>

                <button
                  onClick={() => handleAction('reject')}
                  className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-md transition-all"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Reject Match</span>
                </button>

                <button
                  onClick={() => handleAction('flag')}
                  className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-md transition-all col-span-2"
                >
                  <Flag className="w-3.5 h-3.5" />
                  <span>Flag for Controller Review</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500 font-mono text-xs">
              Select an exception item from the list to review agent reasoning and resolve.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
