import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { MetricCard } from '../components/MetricCard';
import { TrendingUp, ShieldAlert, AlertTriangle, Cpu, DollarSign, Activity } from 'lucide-react';

interface AdvancedAnalyticsProps {
  runId: string;
}

export const AdvancedAnalytics: React.FC<AdvancedAnalyticsProps> = ({ runId }) => {
  const [forecast, setForecast] = useState<any>(null);
  const [anomalies, setAnomalies] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadIntelligence = () => {
    setLoading(true);
    setError(null);

    Promise.all([
      fetch(`/api/runs/${runId}/forecast`).then(async r => {
        if (!r.ok) throw new Error(`Forecast API returned ${r.status}`);
        const json = await r.json();
        if (!json || json.detail || typeof json.projected_30d_balance !== 'number') {
          throw new Error('Forecast data unavailable');
        }
        return json;
      }),
      fetch(`/api/runs/${runId}/anomalies`).then(async r => {
        if (!r.ok) throw new Error(`Anomalies API returned ${r.status}`);
        const json = await r.json();
        if (!json || json.detail || !Array.isArray(json.records)) {
          throw new Error('Anomaly data unavailable');
        }
        return json;
      })
    ])
      .then(([fData, aData]) => {
        setForecast(fData);
        setAnomalies(aData);
      })
      .catch(err => {
        console.error('Intelligence load error:', err);
        setError(err.message || 'Failed to compute predictive models.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (runId) {
      loadIntelligence();
    }
  }, [runId]);

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-400 font-mono space-y-3">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-300">Running predictive financial intelligence & risk models...</p>
        <p className="text-xs text-slate-500">Calculating 30-day forward liquidity curves & structuring anomaly flags.</p>
      </div>
    );
  }

  if (error || !forecast || !anomalies) {
    return (
      <div className="p-8 bg-slate-900 border border-slate-800 rounded-xl text-center space-y-4 max-w-lg mx-auto my-12">
        <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-white">Intelligence Data Unavailable</h3>
        <p className="text-sm text-slate-400 font-mono">
          {error || 'Unable to compute forecast or anomaly scores for the selected run.'}
        </p>
        <button
          onClick={loadIntelligence}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-mono text-xs transition-colors"
        >
          Retry Calculation
        </button>
      </div>
    );
  }


  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Advanced Financial Intelligence & Risk Matrix</h1>
        <p className="text-sm text-slate-400 mt-1">
          30-day liquidity forecasting, working capital velocity, and fraud anomaly detection.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Projected 30-Day Cash"
          value={`$${forecast.projected_30d_balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
          subtitle="Conservative cash projection"
          icon={<TrendingUp className="w-4 h-4" />}
          badgeColor="emerald"
        />
        <MetricCard
          title="Daily Cash Velocity"
          value={`$${forecast.net_daily_velocity.toLocaleString('en-US', { minimumFractionDigits: 2 })}/day`}
          subtitle="Net daily cash movement"
          icon={<Activity className="w-4 h-4" />}
          badgeColor="blue"
        />
        <MetricCard
          title="High Risk Anomalies"
          value={anomalies.high_risk_count}
          subtitle="Structuring & outlier flags"
          icon={<ShieldAlert className="w-4 h-4" />}
          badgeColor="amber"
        />
        <MetricCard
          title="Analyzed Transactions"
          value={anomalies.total_records_analyzed}
          subtitle="Full batch risk scored"
          icon={<Cpu className="w-4 h-4" />}
          badgeColor="purple"
        />
      </div>

      {/* 30-Day Forecast Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
              30-Day Forward Liquidity Forecast Curve
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Conservative (excluding open exceptions) vs. Optimistic (with recoverable items)
            </p>
          </div>
          <div className="font-mono text-xs text-emerald-400">
            Confirmed Start: ${forecast.current_confirmed_balance.toLocaleString()}
          </div>
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={forecast.timeline} margin={{ top: 10, right: 30, left: 20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorCons" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorOpt" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Legend />
              <Area type="monotone" dataKey="conservative_balance" name="Conservative Forecast" stroke="#10b981" fillOpacity={1} fill="url(#colorCons)" />
              <Area type="monotone" dataKey="optimistic_balance" name="Optimistic Forecast" stroke="#3b82f6" fillOpacity={1} fill="url(#colorOpt)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Anomaly & Risk Analysis Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-semibold text-sm text-slate-200 uppercase tracking-wider">
            Automated Anomaly & Fraud Risk Signals
          </h3>
          <span className="text-xs font-mono text-slate-400">
            {anomalies.high_risk_count} High Risk | {anomalies.medium_risk_count} Medium Risk
          </span>
        </div>

        <div className="divide-y divide-slate-800/60">
          {anomalies.records.slice(0, 10).map((r: any) => (
            <div key={r.id} className="p-4 hover:bg-slate-800/40 transition-colors flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-white">{r.record_code || r.record_id}</span>
                  <span className="text-xs font-mono text-slate-400">${r.amount?.toFixed(2)}</span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                    r.risk_level === 'HIGH'
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      : (r.risk_level === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-slate-800 text-slate-400')
                  }`}>
                    RISK: {r.risk_level} ({r.anomaly_score})
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-1 font-mono">{r.counterparty}</div>
              </div>

              <div className="flex items-center gap-1.5 flex-wrap justify-end">
                {r.anomaly_flags?.map((flag: string) => (
                  <span key={flag} className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-amber-400 border border-slate-800">
                    {flag}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
