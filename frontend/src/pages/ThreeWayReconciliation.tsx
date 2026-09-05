import React, { useState } from 'react';
import { MetricCard } from '../components/MetricCard';
import { Layers, ArrowRight, CheckCircle2, ShieldCheck, DollarSign, Cpu } from 'lucide-react';

interface ThreeWayProps {
  runId: string;
}

export const ThreeWayReconciliationView: React.FC<ThreeWayProps> = ({ runId }) => {
  const [activeScenario, setActiveScenario] = useState<number>(0);

  const scenarios = [
    {
      title: "SaaS Subscription Payout (Stripe)",
      ledger: { code: "LED-3WAY-101", ref: "INV-STRIPE-881", gross: 1000.00, date: "2026-08-10", cp: "Stripe Subscriptions" },
      gateway: { code: "GW-STRIPE-881", gross: 1000.00, fee: 29.00, net: 971.00, status: "MATCHED" },
      bank: { code: "BNK-DEP-881", net: 971.00, date: "2026-08-12", cp: "STRIPE PAYOUT DEPOSIT", status: "VERIFIED" },
      feeVariance: "$0.00 (Standard 2.9% Fee)",
      status: "3-WAY MATCH CONFIRMED"
    },
    {
      title: "E-Commerce Bulk Settlement (Razorpay)",
      ledger: { code: "LED-3WAY-102", ref: "INV-RAZOR-902", gross: 4500.00, date: "2026-08-14", cp: "Razorpay Payouts" },
      gateway: { code: "GW-RAZOR-902", gross: 4500.00, fee: 90.00, net: 4410.00, status: "MATCHED" },
      bank: { code: "BNK-DEP-902", net: 4410.00, date: "2026-08-15", cp: "RAZORPAY PAYMENTS", status: "VERIFIED" },
      feeVariance: "$0.00 (Standard 2.0% Fee)",
      status: "3-WAY MATCH CONFIRMED"
    },
    {
      title: "Enterprise Freight Payout (Fee Variance Case)",
      ledger: { code: "LED-3WAY-103", ref: "LOG-3WAY-903", gross: 12500.00, date: "2026-08-18", cp: "Global Freight Payment" },
      gateway: { code: "GW-FREIGHT-903", gross: 12500.00, fee: 362.50, net: 12137.50, status: "MATCHED" },
      bank: { code: "BNK-DEP-903", net: 12137.50, date: "2026-08-20", cp: "GLOBAL FREIGHT WIRE", status: "VERIFIED" },
      feeVariance: "$0.00 (Standard 2.9% Fee)",
      status: "3-WAY MATCH CONFIRMED"
    }
  ];

  const curr = scenarios[activeScenario];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Layers className="w-6 h-6 text-blue-400" />
            3-Way Multi-Feed Reconciliation Layer
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Simultaneous 3-source matching: Internal Ledger vs Payment Processor (Stripe/Razorpay) vs Bank Deposit Statement.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {scenarios.map((sc, idx) => (
            <button
              key={idx}
              onClick={() => setActiveScenario(idx)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
                activeScenario === idx
                  ? 'bg-blue-600 text-white font-bold shadow-lg shadow-blue-600/30'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              Case #{idx + 1}
            </button>
          ))}
        </div>
      </div>

      {/* 3-Column Visual Flow */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Source 1: Internal Ledger */}
        <div className="glass-card rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-3 text-[10px] font-mono font-bold text-blue-400 uppercase bg-blue-500/10 rounded-bl-xl border-l border-b border-blue-500/20">
            Source A: Internal Ledger
          </div>

          <h3 className="text-xs font-mono font-bold uppercase text-slate-400 mb-4">1. Internal Gross Invoice</h3>

          <div className="space-y-3 font-mono">
            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
              <div className="text-[11px] text-slate-500">TRANSACTION CODE:</div>
              <div className="text-sm font-bold text-white">{curr.ledger.code}</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
              <div className="text-[11px] text-slate-500">GROSS AMOUNT RECORDED:</div>
              <div className="text-lg font-extrabold text-blue-400">${curr.ledger.gross.toFixed(2)}</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1 text-slate-300">
              <div>Ref: <span className="font-bold text-white">{curr.ledger.ref}</span></div>
              <div>Date: <span className="font-bold text-slate-400">{curr.ledger.date}</span></div>
              <div>Vendor: <span className="font-bold text-slate-400">{curr.ledger.cp}</span></div>
            </div>
          </div>
        </div>

        {/* Source 2: Payment Gateway */}
        <div className="glass-card rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-3 text-[10px] font-mono font-bold text-indigo-400 uppercase bg-indigo-500/10 rounded-bl-xl border-l border-b border-indigo-500/20">
            Source B: Gateway Feed
          </div>

          <h3 className="text-xs font-mono font-bold uppercase text-slate-400 mb-4">2. Gateway Fee Deductions</h3>

          <div className="space-y-3 font-mono">
            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
              <div className="text-[11px] text-slate-500">GATEWAY SETTLEMENT:</div>
              <div className="text-sm font-bold text-white">{curr.gateway.code}</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
              <div className="flex justify-between text-xs text-slate-400">
                <span>Gross Collected:</span>
                <span className="text-white">${curr.gateway.gross.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-xs text-rose-400">
                <span>Fee Deduction:</span>
                <span>-${curr.gateway.fee.toFixed(2)}</span>
              </div>
              <div className="pt-2 border-t border-slate-800 flex justify-between text-base font-extrabold text-indigo-400">
                <span>Net Gateway Payout:</span>
                <span>${curr.gateway.net.toFixed(2)}</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/30 text-xs text-indigo-300 font-mono text-center font-bold">
              GATEWAY STATUS: {curr.gateway.status}
            </div>
          </div>
        </div>

        {/* Source 3: Bank Deposit */}
        <div className="glass-card rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-3 text-[10px] font-mono font-bold text-emerald-400 uppercase bg-emerald-500/10 rounded-bl-xl border-l border-b border-emerald-500/20">
            Source C: Bank Statement
          </div>

          <h3 className="text-xs font-mono font-bold uppercase text-slate-400 mb-4">3. Bank Net Deposit Received</h3>

          <div className="space-y-3 font-mono">
            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
              <div className="text-[11px] text-slate-500">BANK DEPOSIT CODE:</div>
              <div className="text-sm font-bold text-white">{curr.bank.code}</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
              <div className="text-[11px] text-slate-500">NET CASH DEPOSITED:</div>
              <div className="text-lg font-extrabold text-emerald-400">${curr.bank.net.toFixed(2)}</div>
            </div>

            <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300 font-mono text-center font-bold">
              {curr.status}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
