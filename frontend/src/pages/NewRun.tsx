import React, { useState } from 'react';
import { createRun, generateSyntheticData } from '../api/client';
import { PlayCircle, Database, Settings, Sliders, Check } from 'lucide-react';

interface NewRunProps {
  onRunCreated: (runId: string) => void;
}

export const NewRun: React.FC<NewRunProps> = ({ onRunCreated }) => {
  const [useSynthetic, setUseSynthetic] = useState(true);
  const [sourceAName, setSourceAName] = useState('Internal Ledger');
  const [sourceBName, setSourceBName] = useState('Bank Feed');
  const [amountTol, setAmountTol] = useState(0.50);
  const [dateTolDays, setDateTolDays] = useState(3);
  const [fuzzyThresh, setFuzzyThresh] = useState(0.85);

  const [fileA, setFileA] = useState<File | null>(null);
  const [fileB, setFileB] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatusText('Ingesting records & running autonomous reconciliation engine...');

    try {
      const formData = new FormData();
      formData.append('source_a_name', sourceAName);
      formData.append('source_b_name', sourceBName);
      formData.append('use_synthetic', String(useSynthetic));
      formData.append('amount_tolerance', String(amountTol));
      formData.append('date_tolerance_days', String(dateTolDays));
      formData.append('fuzzy_threshold', String(fuzzyThresh));

      if (!useSynthetic && fileA && fileB) {
        formData.append('file_a', fileA);
        formData.append('file_b', fileB);
      }

      const run = await createRun(formData);
      onRunCreated(run.id);
    } catch (err: any) {
      console.error(err);
      alert('Error launching run: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateSynthetic = async () => {
    try {
      setStatusText('Regenerating 50+ record synthetic dataset with noise...');
      await generateSyntheticData(Math.floor(Math.random() * 1000));
      alert('New synthetic dataset generated in data/synthetic/!');
    } catch (e: any) {
      alert('Failed to generate synthetic data: ' + e.message);
    } finally {
      setStatusText('');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Launch Autonomous Reconciliation</h1>
        <p className="text-sm text-slate-400 mt-1">
          Configure sources and tolerance rules to close a complete reconciliation loop.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Source Mode Selection */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-400" />
            1. Select Data Sources
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              onClick={() => setUseSynthetic(true)}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                useSynthetic
                  ? 'bg-blue-950/40 border-blue-500 text-white'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm">Synthetic Benchmark Dataset</span>
                {useSynthetic && <Check className="w-4 h-4 text-blue-400" />}
              </div>
              <p className="text-xs text-slate-400 mt-2">
                50+ combined records with injected noise (date shifts, rounding, split transactions, duplicates & orphans).
              </p>
              <div className="mt-3 font-mono text-[11px] text-blue-400">
                internal_ledger.csv vs bank_feed.csv
              </div>
            </div>

            <div
              onClick={() => setUseSynthetic(false)}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                !useSynthetic
                  ? 'bg-blue-950/40 border-blue-500 text-white'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm">Upload Custom CSV Feeds</span>
                {!useSynthetic && <Check className="w-4 h-4 text-blue-400" />}
              </div>
              <p className="text-xs text-slate-400 mt-2">
                Upload your own internal ledger and bank statement CSV files for batch matching.
              </p>
              <div className="mt-3 font-mono text-[11px] text-slate-500">
                Requires: record_id, amount, reference_id, transaction_date
              </div>
            </div>
          </div>

          {useSynthetic && (
            <div className="mt-4 p-3 bg-slate-950/60 border border-slate-800 rounded-lg flex items-center justify-between">
              <span className="text-xs text-slate-400 font-mono">
                Dataset seed: 42 (Reproducible 50+ record benchmark)
              </span>
              <button
                type="button"
                onClick={handleRegenerateSynthetic}
                className="text-xs text-blue-400 hover:text-blue-300 font-medium font-mono"
              >
                [Re-roll Synthetic Seed]
              </button>
            </div>
          )}

          {!useSynthetic && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1">Source A (Internal Ledger CSV)</label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={e => setFileA(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-300 bg-slate-950 border border-slate-800 rounded-lg p-2"
                />
              </div>
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1">Source B (Bank Feed CSV)</label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={e => setFileB(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-300 bg-slate-950 border border-slate-800 rounded-lg p-2"
                />
              </div>
            </div>
          )}
        </div>

        {/* Engine Parameters */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-emerald-400" />
            2. Match Engine Tolerance Parameters
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Amount Tolerance ($)</label>
              <input
                type="number"
                step="0.05"
                value={amountTol}
                onChange={e => setAmountTol(parseFloat(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm font-mono text-white focus:outline-none focus:border-blue-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">Tier 1 tolerant amount difference threshold</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Date Window (Days)</label>
              <input
                type="number"
                value={dateTolDays}
                onChange={e => setDateTolDays(parseInt(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm font-mono text-white focus:outline-none focus:border-blue-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">Maximum allowed date drift for matching</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Fuzzy Reference Threshold</label>
              <input
                type="number"
                step="0.05"
                max="1.0"
                min="0.5"
                value={fuzzyThresh}
                onChange={e => setFuzzyThresh(parseFloat(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm font-mono text-white focus:outline-none focus:border-blue-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">String similarity threshold (0.85 = 85%)</p>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-3">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold shadow-lg shadow-blue-600/30 transition-all text-sm disabled:opacity-50"
          >
            <PlayCircle className="w-5 h-5" />
            <span>{loading ? 'Running Engine...' : 'Start Autonomous Reconciliation'}</span>
          </button>
        </div>
      </form>

      {loading && (
        <div className="p-6 bg-blue-950/30 border border-blue-500/30 rounded-xl text-center">
          <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm font-mono text-blue-300">{statusText}</p>
        </div>
      )}
    </div>
  );
};
