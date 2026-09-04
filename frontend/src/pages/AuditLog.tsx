import React, { useEffect, useState } from 'react';
import { getAuditLog } from '../api/client';
import { AuditLogItem } from '../types';
import { History, Bot, User, Clock } from 'lucide-react';

interface AuditLogProps {
  runId: string;
}

export const AuditLogPage: React.FC<AuditLogProps> = ({ runId }) => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAuditLog(runId)
      .then(setLogs)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [runId]);

  if (loading) {
    return <div className="p-8 text-center text-slate-400 font-mono">Loading chronological audit log...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System & Human Audit Trail</h1>
        <p className="text-sm text-slate-400 mt-1">
          Complete immutable event stream for run <span className="font-mono text-blue-400">{runId}</span>.
        </p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="relative border-l-2 border-slate-800 ml-4 space-y-6">
          {logs.map(log => (
            <div key={log.id} className="relative pl-6">
              {/* Timeline marker node */}
              <div className={`absolute -left-[17px] top-0.5 w-8 h-8 rounded-full border flex items-center justify-center ${
                log.actor === 'agent'
                  ? 'bg-blue-950 border-blue-500/50 text-blue-400'
                  : 'bg-emerald-950 border-emerald-500/50 text-emerald-400'
              }`}>
                {log.actor === 'agent' ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
              </div>

              <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-mono text-xs">
                    <span className={`font-bold uppercase ${log.actor === 'agent' ? 'text-blue-400' : 'text-emerald-400'}`}>
                      [{log.actor}]
                    </span>
                    <span className="font-bold text-white">{log.action}</span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                </div>

                {log.details && (
                  <pre className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto">
                    {JSON.stringify(log.details, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
