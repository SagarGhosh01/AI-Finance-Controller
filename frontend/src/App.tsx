import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { NewRun } from './pages/NewRun';
import { RunProgress } from './pages/RunProgress';
import { RunResults } from './pages/RunResults';
import { ExceptionReview } from './pages/ExceptionReview';
import { CashPositionPage } from './pages/CashPosition';
import { AuditLogPage } from './pages/AuditLog';
import { SettingsPage } from './pages/Settings';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [currentRunId, setCurrentRunId] = useState<string | null>(null);

  const handleRunCreated = (runId: string) => {
    setCurrentRunId(runId);
    setActiveTab('progress');
  };

  const handleSelectRun = (runId: string) => {
    setCurrentRunId(runId);
    setActiveTab('run-results');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentRunId={currentRunId}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <Dashboard
            onSelectRun={handleSelectRun}
            onNewRun={() => setActiveTab('new-run')}
          />
        )}

        {activeTab === 'new-run' && (
          <NewRun onRunCreated={handleRunCreated} />
        )}

        {activeTab === 'progress' && currentRunId && (
          <RunProgress
            runId={currentRunId}
            onComplete={() => setActiveTab('run-results')}
          />
        )}

        {activeTab === 'run-results' && currentRunId && (
          <RunResults
            runId={currentRunId}
            onNavigateToExceptions={() => setActiveTab('exceptions')}
            onNavigateToCashPosition={() => setActiveTab('cash-position')}
          />
        )}

        {activeTab === 'exceptions' && currentRunId && (
          <ExceptionReview runId={currentRunId} />
        )}

        {activeTab === 'cash-position' && currentRunId && (
          <CashPositionPage runId={currentRunId} />
        )}

        {activeTab === 'audit' && currentRunId && (
          <AuditLogPage runId={currentRunId} />
        )}

        {activeTab === 'settings' && (
          <SettingsPage />
        )}
      </main>

      <footer className="bg-slate-900 border-t border-slate-800 py-4 text-center text-xs font-mono text-slate-500">
        Demo data & synthetic engine — not real financial records. Fincheck AI Autonomous Verification Layer v1.0.
      </footer>
    </div>
  );
}
export default App;
