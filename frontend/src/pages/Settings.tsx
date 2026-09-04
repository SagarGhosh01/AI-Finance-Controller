import React from 'react';
import { Settings as SettingsIcon, Key, Shield, Sliders, Database } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System Settings & Governance</h1>
        <p className="text-sm text-slate-400 mt-1">
          Configure API credentials, feature flags, and engine defaults.
        </p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
        <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2 border-b border-slate-800 pb-3">
          <Key className="w-4 h-4 text-purple-400" />
          LLM Provider Configuration
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
          <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
            <div className="text-slate-400">LLM PROVIDER:</div>
            <div className="text-sm font-bold text-white">Anthropic Claude (Messages API)</div>
            <div className="text-slate-500">Model: claude-3-haiku-20240307 / low temp (0.1)</div>
          </div>

          <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
            <div className="text-slate-400">API KEY STATUS:</div>
            <div className="text-sm font-bold text-emerald-400">ENVIRONMENT CONFIGURED OR FALLBACK ACTIVE</div>
            <div className="text-slate-500">Structured JSON Output tool-use enabled</div>
          </div>
        </div>

        <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2 border-b border-slate-800 pb-3 pt-4">
          <Shield className="w-4 h-4 text-blue-400" />
          Feature Flags & Governance
        </h2>

        <div className="space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between p-3 bg-slate-950 border border-slate-800 rounded-lg">
            <div>
              <div className="font-bold text-white">AUTH_ENABLED</div>
              <div className="text-slate-500 text-[11px]">JWT authentication layer (default off for demo)</div>
            </div>
            <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">FALSE</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-950 border border-slate-800 rounded-lg">
            <div>
              <div className="font-bold text-white">RECORD_CONSERVATION_INVARIANT</div>
              <div className="text-slate-500 text-[11px]">Strict assertion that matched + exceptions == total</div>
            </div>
            <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">ACTIVE (STRICT)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
