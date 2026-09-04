import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: string;
  badgeColor?: 'blue' | 'emerald' | 'amber' | 'purple';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  badgeColor = 'blue'
}) => {
  const colorStyles = {
    blue: 'border-blue-500/20 text-blue-400 bg-blue-500/10',
    emerald: 'border-emerald-500/20 text-emerald-400 bg-emerald-500/10',
    amber: 'border-amber-500/20 text-amber-400 bg-amber-500/10',
    purple: 'border-purple-500/20 text-purple-400 bg-purple-500/10',
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm hover:border-slate-700 transition-all">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</span>
        {icon && (
          <div className={`p-2 rounded-lg border ${colorStyles[badgeColor]}`}>
            {icon}
          </div>
        )}
      </div>
      <div className="mt-3">
        <div className="text-2xl font-bold font-mono tracking-tight text-white">{value}</div>
        {subtitle && <div className="text-xs text-slate-400 mt-1 font-mono">{subtitle}</div>}
      </div>
    </div>
  );
};
