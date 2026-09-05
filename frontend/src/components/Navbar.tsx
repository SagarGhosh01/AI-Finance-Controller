import React from 'react';
import { ShieldCheck, PlayCircle, BarChart3, Settings as SettingsIcon, DollarSign, History, Layers, TrendingUp, FileSpreadsheet } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  currentRunId: string | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, currentRunId }) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-blue-600/30">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400 bg-clip-text text-transparent">
                FINCHECK AI
              </span>
              <span className="text-[10px] block font-mono text-slate-400 uppercase tracking-widest -mt-1">
                Autonomous Verification Engine
              </span>
            </div>
          </div>

          <nav className="flex items-center gap-1 sm:gap-2">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'dashboard'
                  ? 'bg-slate-800 text-blue-400 border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => setActiveTab('new-run')}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'new-run'
                  ? 'bg-slate-800 text-blue-400 border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <PlayCircle className="w-4 h-4" />
              <span>New Run</span>
            </button>

            {currentRunId && (
              <>
                <button
                  onClick={() => setActiveTab('run-results')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'run-results'
                      ? 'bg-slate-800 text-blue-400 border border-slate-700'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Layers className="w-4 h-4" />
                  <span>Run Results</span>
                </button>

                <button
                  onClick={() => setActiveTab('exceptions')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'exceptions'
                      ? 'bg-slate-800 text-amber-400 border border-slate-700'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span>Exceptions</span>
                </button>

                <button
                  onClick={() => setActiveTab('3way')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    activeTab === '3way'
                      ? 'bg-slate-800 text-blue-400 border border-slate-700 shadow-md'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Layers className="w-4 h-4" />
                  <span>3-Way Match</span>
                </button>

                <button
                  onClick={() => setActiveTab('insights')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    activeTab === 'insights'
                      ? 'bg-slate-800 text-emerald-400 border border-slate-700 shadow-md'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Excel Report</span>
                </button>

                <button
                  onClick={() => setActiveTab('cash-position')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    activeTab === 'cash-position'
                      ? 'bg-slate-800 text-emerald-400 border border-slate-700 shadow-md'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <DollarSign className="w-4 h-4" />
                  <span>Cash Position</span>
                </button>

                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'analytics'
                      ? 'bg-slate-800 text-indigo-400 border border-slate-700'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <TrendingUp className="w-4 h-4" />
                  <span>Intelligence</span>
                </button>

                <button
                  onClick={() => setActiveTab('audit')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'audit'
                      ? 'bg-slate-800 text-purple-400 border border-slate-700'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <History className="w-4 h-4" />
                  <span>Audit Trail</span>
                </button>
              </>
            )}

            <button
              onClick={() => setActiveTab('settings')}
              className={`p-2 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors ${
                activeTab === 'settings' ? 'bg-slate-800 text-slate-200' : ''
              }`}
              title="Settings"
            >
              <SettingsIcon className="w-4 h-4" />
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
