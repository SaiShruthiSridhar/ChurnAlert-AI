import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const API_BASE = 'http://localhost:5000';

export default function Chatbot({ selectedAccountId }) {
  const [isOpen, setIsOpen] = useState(false);
  const [mode, setMode] = useState('assistant'); // 'general' or 'assistant'
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm your ChurnAI assistant. How can I help you today?", sender: 'bot', time: new Date() }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { id: Date.now(), text: input, sender: 'user', time: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      if (mode === 'assistant' && selectedAccountId) {
        // Use the new conversational chat endpoint
        const response = await axios.post(`${API_BASE}/chat`, {
          account_id: selectedAccountId,
          query: input
        });
        const botMsg = { 
          id: Date.now() + 1, 
          text: response.data.response, 
          sender: 'bot', 
          time: new Date() 
        };
        setMessages(prev => [...prev, botMsg]);
      } else {
        // Simple mock for general mode
        setTimeout(() => {
          const botMsg = { 
            id: Date.now() + 1, 
            text: "That's an interesting question about churn management. In general, proactive outreach and feature adoption tracking are key strategies.", 
            sender: 'bot', 
            time: new Date() 
          };
          setMessages(prev => [...prev, botMsg]);
          setIsTyping(false);
        }, 1000);
        return;
      }
    } catch (err) {
      const errorMsg = { id: Date.now() + 1, text: "I'm having trouble connecting to the brain. Please try again later.", sender: 'bot', time: new Date() };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="fixed bottom-8 right-8 z-[1000]">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="mb-4 w-96 h-[500px] bg-white rounded-3xl shadow-2xl border border-slate-100 flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="p-4 bg-indigo-600 text-white flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                  <Bot className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-black text-sm leading-none mb-1">ChurnAI Bot</h3>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => setMode('assistant')}
                      className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded ${mode === 'assistant' ? 'bg-white text-indigo-600' : 'bg-indigo-500 text-indigo-100'}`}
                    >
                      Assistant
                    </button>
                    <button 
                      onClick={() => setMode('general')}
                      className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded ${mode === 'general' ? 'bg-white text-indigo-600' : 'bg-indigo-500 text-indigo-100'}`}
                    >
                      General
                    </button>
                  </div>
                </div>
              </div>
              <button onClick={() => setIsOpen(false)} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 custom-scrollbar">
              {messages.map(msg => (
                <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-3 rounded-2xl text-sm prose-sm ${
                    msg.sender === 'user' 
                      ? 'bg-indigo-600 text-white rounded-tr-none' 
                      : 'bg-white text-slate-700 shadow-sm border border-slate-100 rounded-tl-none'
                  }`}>
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white p-3 rounded-2xl rounded-tl-none border border-slate-100 flex gap-1">
                    <span className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce"></span>
                    <span className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce delay-100"></span>
                    <span className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce delay-200"></span>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="p-4 bg-white border-t border-slate-100 flex flex-col gap-2">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '10px' }}>
                <p style={{ fontSize: '10px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.08em', margin: 0 }}>Suggested Questions</p>
                {[
                  'Why is this account flagged?',
                  'What worked for similar accounts?',
                  'When should I follow up?'
                ].map((q, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setInput(q)}
                    style={{
                      padding: '8px 12px', background: '#f8fafc',
                      border: '1px solid #e2e8f0', borderRadius: '10px',
                      fontSize: '11px', fontWeight: 600, color: '#475569',
                      cursor: 'pointer', textAlign: 'left', transition: 'all 0.15s'
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = '#eef2ff'; e.currentTarget.style.color = '#6366f1'; }}
                    onMouseLeave={e => { e.currentTarget.style.background = '#f8fafc'; e.currentTarget.style.color = '#475569'; }}
                  >
                    {q}
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <input 
                  type="text" 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={mode === 'assistant' ? "Ask about selected account..." : "Ask a general question..."}
                  className="flex-1 bg-slate-50 border-none outline-none px-4 py-2 rounded-xl text-sm font-medium text-slate-600 focus:ring-2 focus:ring-indigo-100"
                />
                <button type="submit" className="p-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100">
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className="w-16 h-16 bg-indigo-600 rounded-full shadow-2xl flex items-center justify-center text-white relative"
      >
        {isOpen ? <X className="w-8 h-8" /> : <MessageSquare className="w-8 h-8" />}
        {!isOpen && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-rose-500 rounded-full border-4 border-white flex items-center justify-center">
            <span className="w-1.5 h-1.5 bg-white rounded-full animate-ping"></span>
          </span>
        )}
      </motion.button>
    </div>
  );
}
