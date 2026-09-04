import React, { useState } from 'react';
import { Bot, Send, X, Sparkles, MessageSquare, CornerDownRight } from 'lucide-react';

interface AICopilotDrawerProps {
  runId: string;
}

export const AICopilotDrawer: React.FC<AICopilotDrawerProps> = ({ runId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'copilot'; text: string; source?: string }>>([
    {
      sender: 'copilot',
      text: `Hello! 👋 I am your AI Financial Controller Copilot for run ${runId.substring(0, 8)}. Ask me anything about reconciliation results, exception reasoning, risk anomalies, or cash forecasts!`
    }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (textToSend?: string) => {
    const q = textToSend || query;
    if (!q.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: q }]);
    if (!textToSend) setQuery('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('query', q);

      const res = await fetch(`/api/runs/${runId}/copilot`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      setMessages(prev => [
        ...prev,
        {
          sender: 'copilot',
          text: data.answer || 'Query processed.',
          source: data.source
        }
      ]);
    } catch (e: any) {
      setMessages(prev => [
        ...prev,
        { sender: 'copilot', text: 'Error connecting to AI Copilot engine: ' + e.message }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Helper to render basic formatting (bold text & linebreaks)
  const renderFormattedText = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, i) => {
      // Process bold **text**
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <React.Fragment key={i}>
          {parts.map((part, pIdx) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return <strong key={pIdx} className="font-bold text-white">{part.slice(2, -2)}</strong>;
            }
            return part;
          })}
          {i < lines.length - 1 && <br />}
        </React.Fragment>
      );
    });
  };

  return (
    <>
      {/* Floating Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-full bg-blue-600 hover:bg-blue-500 text-white font-semibold shadow-2xl shadow-blue-600/50 transition-all border border-blue-400/40"
        >
          <Bot className="w-5 h-5 text-white" />
          <span className="text-xs font-mono">Ask AI Copilot</span>
          <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
        </button>
      )}

      {/* Copilot Drawer Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-[420px] max-w-[calc(100vw-2rem)] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[540px]">
          {/* Header */}
          <div className="px-4 py-3 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white tracking-wide">AI FINANCE COPILOT</h4>
                <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  Online & Context-Aware
                </span>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Quick Query Chips */}
          <div className="px-3 py-2 bg-slate-950/60 border-b border-slate-800/80 flex items-center gap-1.5 overflow-x-auto text-[10px] font-mono">
            <button
              onClick={() => handleSend('Hi!')}
              className="px-2.5 py-1 rounded-full bg-slate-800 text-blue-300 hover:bg-slate-700 whitespace-nowrap font-medium"
            >
              👋 Greeting
            </button>
            <button
              onClick={() => handleSend('Why are items in review?')}
              className="px-2.5 py-1 rounded-full bg-slate-800 text-amber-300 hover:bg-slate-700 whitespace-nowrap font-medium"
            >
              🔍 Exceptions
            </button>
            <button
              onClick={() => handleSend('What is our cash position?')}
              className="px-2.5 py-1 rounded-full bg-slate-800 text-emerald-300 hover:bg-slate-700 whitespace-nowrap font-medium"
            >
              💰 Cash Balance
            </button>
            <button
              onClick={() => handleSend('Show fraud risk anomalies')}
              className="px-2.5 py-1 rounded-full bg-slate-800 text-purple-300 hover:bg-slate-700 whitespace-nowrap font-medium"
            >
              🛡️ Risk Outliers
            </button>
          </div>

          {/* Message Stream */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 font-sans text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-2 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'copilot' && (
                  <div className="w-6 h-6 rounded bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                )}
                <div
                  className={`p-3 rounded-xl max-w-[85%] ${
                    m.sender === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none font-medium'
                      : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-bl-none font-mono text-[11px] leading-relaxed'
                  }`}
                >
                  {renderFormattedText(m.text)}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-2 items-center text-slate-400 text-xs font-mono">
                <Bot className="w-4 h-4 animate-bounce text-blue-400" />
                <span>Copilot reasoning over financial records...</span>
              </div>
            )}
          </div>

          {/* Input Footer */}
          <form
            onSubmit={e => {
              e.preventDefault();
              handleSend();
            }}
            className="p-3 bg-slate-950 border-t border-slate-800 flex items-center gap-2"
          >
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Ask Copilot any financial question..."
              className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="p-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
};
