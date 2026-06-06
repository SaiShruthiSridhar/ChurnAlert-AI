import { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, LineChart, Line } from 'recharts';
import { LayoutDashboard, TrendingUp, Users, DollarSign, ArrowLeft, ShieldAlert, ShieldCheck, Bot } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

const API_BASE = 'http://localhost:5000';

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [aiInsight, setAiInsight] = useState('');
  const [loading, setLoading] = useState(true);
  const [trendData, setTrendData] = useState([]);
  const [outcomes, setOutcomes] = useState(null);
  const [dataSource] = useState(() => localStorage.getItem('analytics_source') || 'csv');

  useEffect(() => {
    fetchStats();
    fetchAiInsights();
    fetchTrends();
    fetchOutcomes();
  }, []);

  const fetchStats = async () => {
    try {
      const source = localStorage.getItem('analytics_source') || 'csv';
      const response = await axios.get(`${API_BASE}/analytics?source=${source}`);
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching analytics:", error);
      setLoading(false);
    }
  };

  const fetchAiInsights = async () => {
    try {
      const source = localStorage.getItem('analytics_source') || 'csv';
      const response = await axios.get(`${API_BASE}/analytics/ai-insights?source=${source}`);
      setAiInsight(response.data.summary);
    } catch (error) {
      console.error("Error fetching AI insights:", error);
    }
  };

  const fetchTrends = async () => {
    try {
      const response = await axios.get(`${API_BASE}/analytics/trends`);
      setTrendData(response.data.trend_data || []);
    } catch (error) {
      console.error("Error fetching trends:", error);
    }
  };

  const fetchOutcomes = async () => {
    try {
      const response = await axios.get(`${API_BASE}/analytics/outcomes`);
      setOutcomes(response.data);
    } catch (error) {
      console.error("Error fetching outcomes:", error);
    }
  };

  if (loading || !stats) {
    return (
      <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  const riskData = [
    { name: 'High Risk', value: stats.risk_distribution.HIGH, color: '#f43f5e' },
    { name: 'Medium Risk', value: stats.risk_distribution.MEDIUM, color: '#f59e0b' },
    { name: 'Low Risk', value: stats.risk_distribution.LOW, color: '#10b981' },
  ];

  const csmData = Object.entries(stats.csm_distribution).map(([name, count]) => ({
    name: name.split(' ')[0],
    accounts: count
  }));

  const downloadReport = () => {
    const reportData = {
      timestamp: new Date().toISOString(),
      summary: stats,
      risk_tiers: riskData,
      workload: csmData
    };
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ChurnAI_Report_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] p-6 lg:p-10">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-10">
          <div>
            <Link to="/dashboard" className="flex items-center gap-2 text-slate-400 hover:text-indigo-600 transition-colors font-bold mb-4">
              <ArrowLeft className="w-4 h-4" /> Back to Dashboard
            </Link>
            <h1 className="text-4xl font-black text-slate-900 tracking-tight">System <span className="text-indigo-600">Analytics</span></h1>
            <p className="text-slate-500 font-medium">Real-time portfolio health and risk assessment metrics.</p>
          </div>
          <div className="flex gap-4">
            <div className="bg-white p-4 rounded-3xl border border-slate-100 shadow-sm text-center min-w-[140px]">
              <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">Portfolio MRR</p>
              <p className="text-2xl font-black text-slate-900">${(stats.total_revenue / 1000).toFixed(1)}k</p>
            </div>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <StatCard icon={<Users className="text-indigo-600" />} label="Total Accounts Monitored" value={stats.total_accounts} color="bg-indigo-50" />
          <StatCard icon={<ShieldAlert className="text-rose-600" />} label="HIGH Risk — Needs Action Now" value={stats.risk_distribution.HIGH} color="bg-rose-50" />
          <StatCard icon={<ShieldCheck className="text-emerald-600" />} label="Healthy — No Action Needed" value={stats.risk_distribution.LOW} color="bg-emerald-50" />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Risk Distribution */}
          <div className="bg-white p-8 rounded-[32px] border border-slate-100 shadow-sm">
            <h3 className="text-lg font-black text-slate-800 mb-8 flex items-center gap-3">
              <span className="w-2 h-6 bg-rose-500 rounded-full"></span>
              Risk Tier Distribution — Who Needs Attention?
            </h3>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    innerRadius={80}
                    outerRadius={120}
                    paddingAngle={8}
                    dataKey="value"
                  >
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                  />
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* CSM Workload */}
          <div className="bg-white p-8 rounded-[32px] border border-slate-100 shadow-sm">
            <h3 className="text-lg font-black text-slate-800 mb-8 flex items-center gap-3">
              <span className="w-2 h-6 bg-indigo-500 rounded-full"></span>
              CSM Workload — Accounts Per Manager
            </h3>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={csmData}>
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 700, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 700, fill: '#64748b' }} />
                  <Tooltip 
                    cursor={{ fill: '#f1f5f9' }}
                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                  />
                  <Bar dataKey="accounts" fill="#4f46e5" radius={[10, 10, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Outcomes + Trend Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          {/* Intervention Outcomes by Month */}
          <div className="bg-white p-8 rounded-[32px] border border-slate-100 shadow-sm">
            <h3 className="text-lg font-black text-slate-800 mb-2 flex items-center gap-3">
              <span className="w-2 h-6 bg-emerald-500 rounded-full"></span>
              Monthly Outcomes — Renewals vs Churned
            </h3>
            <p className="text-xs text-slate-400 font-medium mb-6">Successful renewals vs churned accounts after CSM outreach</p>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendData} barSize={20}>
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 700, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 700, fill: '#64748b' }} />
                  <Tooltip
                    cursor={{ fill: '#f1f5f9' }}
                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                  />
                  <Legend verticalAlign="bottom" height={36} />
                  <Bar dataKey="successful" name="Successful Renewals" fill="#10b981" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="failed" name="Churned" fill="#f43f5e" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            {outcomes && (
              <div className="mt-4 flex gap-4 justify-center">
                <div className="text-center px-4 py-2 bg-emerald-50 rounded-2xl">
                  <p className="text-[10px] text-emerald-600 font-black uppercase tracking-widest">Success Rate</p>
                  <p className="text-2xl font-black text-emerald-600">{outcomes.success_rate}%</p>
                </div>
                <div className="text-center px-4 py-2 bg-indigo-50 rounded-2xl">
                  <p className="text-[10px] text-indigo-600 font-black uppercase tracking-widest">Total Interventions</p>
                  <p className="text-2xl font-black text-indigo-600">{outcomes.total_interventions}</p>
                </div>
              </div>
            )}
          </div>

          {/* Churn Risk Trend */}
          <div className="bg-white p-8 rounded-[32px] border border-slate-100 shadow-sm">
            <h3 className="text-lg font-black text-slate-800 mb-2 flex items-center gap-3">
              <span className="w-2 h-6 bg-amber-500 rounded-full"></span>
              6-Month Risk Trend — Are Things Getting Better?
            </h3>
            <p className="text-xs text-slate-400 font-medium mb-6">Risk tier distribution over the last 6 months</p>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 700, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 700, fill: '#64748b' }} />
                  <Tooltip
                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                  />
                  <Legend verticalAlign="bottom" height={36} />
                  <Line type="monotone" dataKey="high_risk" name="High Risk" stroke="#f43f5e" strokeWidth={3} dot={{ fill: '#f43f5e', r: 4 }} />
                  <Line type="monotone" dataKey="medium_risk" name="Medium Risk" stroke="#f59e0b" strokeWidth={3} dot={{ fill: '#f59e0b', r: 4 }} />
                  <Line type="monotone" dataKey="low_risk" name="Low Risk" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Projections or Trend - Placeholder */}
        <div className="mt-8 bg-gradient-to-br from-slate-900 to-indigo-950 p-10 rounded-[40px] text-white overflow-hidden relative">
          <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 blur-[100px] rounded-full translate-x-20 -translate-y-20"></div>
          <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-10">
            <div>
              <h2 className="text-3xl font-black mb-4 flex items-center gap-3">
                <Bot className="w-8 h-8 text-indigo-400" />
                Portfolio AI Agent
              </h2>
              <div className="text-slate-300 max-w-4xl font-medium leading-relaxed text-sm lg:text-base prose prose-invert prose-sm">
                <ReactMarkdown>
                  {aiInsight || "Analyzing portfolio-wide risk factors..."}
                </ReactMarkdown>
              </div>
            </div>
            <button 
              onClick={downloadReport}
              className="px-8 py-4 bg-white text-slate-900 font-black rounded-2xl hover:scale-105 transition-transform shadow-xl"
            >
              Download Full Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm flex items-center gap-6"
    >
      <div className={`w-16 h-16 ${color} rounded-2xl flex items-center justify-center`}>
        {icon}
      </div>
      <div>
        <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">{label}</p>
        <p className="text-3xl font-black text-slate-900 leading-none">{value}</p>
      </div>
    </motion.div>
  );
}
