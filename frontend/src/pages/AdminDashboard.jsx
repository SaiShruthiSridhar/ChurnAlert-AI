import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const API_BASE = 'http://localhost:5000';

const getTierColor = (tier) => {
  switch (tier) {
    case 'HIGH': return { color: '#dc2626', bg: '#fef2f2', border: '#fecaca' };
    case 'MEDIUM': return { color: '#d97706', bg: '#fffbeb', border: '#fde68a' };
    case 'LOW': return { color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0' };
    default: return { color: '#64748b', bg: '#f8fafc', border: '#e2e8f0' };
  }
};

export default function AdminDashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [outcomes, setOutcomes] = useState(null);
  const [thresholds, setThresholds] = useState([]);
  const [thresholdValues, setThresholdValues] = useState({});
  const [editingThreshold, setEditingThreshold] = useState(null);
  const [thresholdSaved, setThresholdSaved] = useState(null);
  const [thresholdError, setThresholdError] = useState(null);
  const userName = localStorage.getItem('user_name') || 'Admin';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const source = localStorage.getItem('analytics_source') || 'csv';
        const [analyticsRes, accountsRes, outcomesRes, thresholdsRes] = await Promise.all([
          axios.get(`${API_BASE}/analytics?source=${source}`),
          axios.get(`${API_BASE}/accounts?source=${source}`),
          axios.get(`${API_BASE}/analytics/outcomes?source=${source}`),
          axios.get(`${API_BASE}/admin/thresholds`).catch(() => ({ data: { thresholds: [] } }))
        ]);
        setAnalytics(analyticsRes.data);
        setAccounts(accountsRes.data);
        setOutcomes(outcomesRes.data);
        const tList = thresholdsRes.data.thresholds || [];
        setThresholds(tList);
        const vals = {};
        tList.forEach(t => { vals[t.rule_name] = t.value; });
        setThresholdValues(vals);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  const handleSaveThreshold = async (ruleName) => {
    const val = thresholdValues[ruleName];
    if (val === undefined || val === '') return;
    try {
      await axios.put(`${API_BASE}/admin/thresholds/${ruleName}`, { value: parseFloat(val) });
      setThresholdSaved(ruleName);
      setThresholdError(null);
      setEditingThreshold(null);
      setTimeout(() => setThresholdSaved(null), 2500);
    } catch (err) {
      setThresholdError(ruleName);
      setTimeout(() => setThresholdError(null), 3000);
    }
  };

  const filteredAccounts = accounts.filter(acc =>
    acc.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    acc.assigned_csm?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    acc.id?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: '#f8fafc', fontFamily: 'Inter, sans-serif'
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{
          width: 48, height: 48, border: '3px solid #e2e8f0', borderTopColor: '#6366f1',
          borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 16px'
        }} />
        <p style={{ color: '#64748b', fontWeight: 700 }}>Loading admin dashboard...</p>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );

  const highRisk = accounts.filter(a => a.risk_tier === 'HIGH').length;
  const medRisk = accounts.filter(a => a.risk_tier === 'MEDIUM').length;
  const lowRisk = accounts.filter(a => a.risk_tier === 'LOW').length;
  const totalRevenue = accounts.reduce((sum, a) => sum + (Number(a.monthly_charges) || 0), 0);

  const statCards = [
    { label: 'Total Accounts', value: analytics?.total_accounts || accounts.length, color: '#6366f1', bg: '#eef2ff', icon: '📊' },
    { label: 'High Risk', value: highRisk, color: '#dc2626', bg: '#fef2f2', icon: '🔴' },
    { label: 'Medium Risk', value: medRisk, color: '#d97706', bg: '#fffbeb', icon: '🟡' },
    { label: 'Healthy / Low Risk', value: lowRisk, color: '#16a34a', bg: '#f0fdf4', icon: '🟢' },
    { label: 'Monthly Revenue', value: `$${Math.round(totalRevenue).toLocaleString()}`, color: '#0891b2', bg: '#ecfeff', icon: '💰' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc', fontFamily: 'Inter, sans-serif' }}>
      {/* Background gradient blobs */}
      <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', overflow: 'hidden', zIndex: 0 }}>
        <div style={{ position: 'absolute', top: '-10%', right: '-5%', width: '40%', height: '40%', background: 'rgba(99,102,241,0.07)', borderRadius: '50%', filter: 'blur(80px)' }} />
        <div style={{ position: 'absolute', bottom: '-10%', left: '-5%', width: '35%', height: '35%', background: 'rgba(168,85,247,0.06)', borderRadius: '50%', filter: 'blur(80px)' }} />
      </div>

      <div style={{ position: 'relative', zIndex: 1, maxWidth: 1400, margin: '0 auto', padding: '32px 24px' }}>

        {/* Header */}
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 40, flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
              <div style={{ width: 48, height: 48, background: '#6366f1', borderRadius: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 8px 24px rgba(99,102,241,0.25)' }}>
                <span style={{ fontSize: 22, fontWeight: 900, color: '#fff', fontStyle: 'italic' }}>C</span>
              </div>
              <div>
                <div style={{ fontSize: 20, fontWeight: 900, color: '#0f172a', letterSpacing: '-0.5px', lineHeight: 1 }}>ChurnAlert <span style={{ color: '#6366f1' }}>AI</span></div>
                <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.15em', marginTop: 2 }}>Admin Dashboard</div>
              </div>
            </Link>
            <div style={{ height: 36, width: 1, background: '#e2e8f0', margin: '0 8px' }} />
            <div style={{ padding: '4px 14px', background: '#ede9fe', border: '1px solid #ddd6fe', borderRadius: 8, fontSize: 11, fontWeight: 800, color: '#7c3aed', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Admin View
            </div>
            <button
              onClick={() => {
                const current = localStorage.getItem('analytics_source') || 'csv';
                const next = current === 'hubspot' ? 'csv' : 'hubspot';
                localStorage.setItem('analytics_source', next);
                window.location.reload();
              }}
              style={{
                padding: '4px 14px',
                background: localStorage.getItem('analytics_source') === 'hubspot' ? '#fff7ed' : '#eef2ff',
                border: `1px solid ${localStorage.getItem('analytics_source') === 'hubspot' ? '#fed7aa' : '#c7d2fe'}`,
                borderRadius: 8, fontSize: 11, fontWeight: 800,
                color: localStorage.getItem('analytics_source') === 'hubspot' ? '#ea580c' : '#6366f1',
                textTransform: 'uppercase', letterSpacing: '0.1em',
                cursor: 'pointer'
              }}
            >
              {localStorage.getItem('analytics_source') === 'hubspot' ? '🔗 HubSpot' : '📊 CSV Demo'}
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 14, fontWeight: 800, color: '#0f172a', lineHeight: 1 }}>{userName}</div>
              <div style={{ fontSize: 11, color: '#6366f1', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 2 }}>System Administrator</div>
            </div>
            <div style={{ width: 44, height: 44, borderRadius: 14, background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', padding: 2, boxShadow: '0 4px 12px rgba(99,102,241,0.3)' }}>
              <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${userName}`} alt="Avatar" style={{ width: '100%', height: '100%', borderRadius: 12, background: '#fff' }} />
            </div>
            <button
              onClick={handleLogout}
              style={{ padding: '10px 20px', background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, fontSize: 13, fontWeight: 700, color: '#64748b', cursor: 'pointer', boxShadow: '0 1px 4px rgba(0,0,0,0.06)', transition: 'all 0.2s' }}
              onMouseEnter={e => { e.target.style.color = '#dc2626'; e.target.style.borderColor = '#fecaca'; }}
              onMouseLeave={e => { e.target.style.color = '#64748b'; e.target.style.borderColor = '#e2e8f0'; }}
            >
              Logout
            </button>
          </div>
        </header>

        {/* Page title */}
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 900, color: '#0f172a', letterSpacing: '-0.5px', marginBottom: 6 }}>Team Portfolio Overview</h1>
          <p style={{ fontSize: 14, color: '#64748b', fontWeight: 500 }}>Real-time churn risk across all CSM accounts</p>
        </div>

        {/* Top Outcome Summary */}
        {outcomes && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 24 }}>
            {[
              { label: 'Interventions This Month', value: outcomes.total_interventions, color: '#6366f1', bg: 'linear-gradient(135deg, #eef2ff, #e0e7ff)', icon: '🎯' },
              { label: 'Successful Renewals', value: outcomes.successful, color: '#16a34a', bg: 'linear-gradient(135deg, #f0fdf4, #dcfce7)', icon: '✅' },
              { label: 'Churned Despite Action', value: outcomes.failed, color: '#dc2626', bg: 'linear-gradient(135deg, #fef2f2, #fee2e2)', icon: '❌' },
            ].map((item, i) => (
              <div key={i} style={{ background: item.bg, borderRadius: 24, padding: '20px 24px', display: 'flex', alignItems: 'center', gap: 16 }}>
                <div style={{ fontSize: 32 }}>{item.icon}</div>
                <div>
                  <p style={{ fontSize: 10, color: item.color, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.1em', margin: '0 0 4px 0', opacity: 0.8 }}>{item.label}</p>
                  <p style={{ fontSize: 36, fontWeight: 900, color: item.color, margin: 0, letterSpacing: '-1px', lineHeight: 1 }}>{item.value}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Stat cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 32 }}>
          {statCards.map((card, i) => (
            <div key={i} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 24, padding: '20px 24px', boxShadow: '0 1px 8px rgba(0,0,0,0.04)', transition: 'box-shadow 0.2s' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: card.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>{card.icon}</div>
                <p style={{ fontSize: 10, color: '#94a3b8', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', margin: 0 }}>{card.label}</p>
              </div>
              <p style={{ fontSize: 32, fontWeight: 900, color: card.color, margin: 0, letterSpacing: '-1px', lineHeight: 1 }}>{card.value}</p>
            </div>
          ))}
        </div>

        {/* Middle row: CSM workload + Risk distribution */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 32 }}>
          {/* CSM Workload */}
          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 28, padding: 28, boxShadow: '0 1px 8px rgba(0,0,0,0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
              <div style={{ width: 4, height: 20, background: '#6366f1', borderRadius: 4 }} />
              <h3 style={{ fontSize: 12, fontWeight: 800, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.12em', margin: 0 }}>CSM Workload Distribution</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {analytics?.csm_distribution && Object.entries(analytics.csm_distribution).sort((a,b) => b[1]-a[1]).map(([csm, count], i) => {
                const maxCount = Math.max(...Object.values(analytics.csm_distribution));
                const pct = Math.round((count / maxCount) * 100);
                return (
                  <div key={i}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: '#334155' }}>{csm}</span>
                      <span style={{ fontSize: 12, fontWeight: 800, color: '#6366f1' }}>{count} accounts</span>
                    </div>
                    <div style={{ height: 6, background: '#f1f5f9', borderRadius: 8, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${pct}%`, background: 'linear-gradient(90deg, #6366f1, #8b5cf6)', borderRadius: 8, transition: 'width 0.8s ease' }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Risk Distribution */}
          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 28, padding: 28, boxShadow: '0 1px 8px rgba(0,0,0,0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
              <div style={{ width: 4, height: 20, background: '#dc2626', borderRadius: 4 }} />
              <h3 style={{ fontSize: 12, fontWeight: 800, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.12em', margin: 0 }}>Risk Distribution</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {[
                { label: 'HIGH', count: highRisk, color: '#dc2626', bg: '#fef2f2', bar: '#dc2626' },
                { label: 'MEDIUM', count: medRisk, color: '#d97706', bg: '#fffbeb', bar: '#f59e0b' },
                { label: 'LOW', count: lowRisk, color: '#16a34a', bg: '#f0fdf4', bar: '#22c55e' }
              ].map((tier, i) => {
                const total = accounts.length || 1;
                const pct = Math.round((tier.count / total) * 100);
                return (
                  <div key={i}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ padding: '2px 10px', background: tier.bg, color: tier.color, fontWeight: 900, fontSize: 10, borderRadius: 6, letterSpacing: '0.08em' }}>{tier.label}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: 20, fontWeight: 900, color: tier.color }}>{tier.count}</span>
                        <span style={{ fontSize: 11, color: '#94a3b8', fontWeight: 600 }}>({pct}%)</span>
                      </div>
                    </div>
                    <div style={{ height: 8, background: '#f1f5f9', borderRadius: 8, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${pct}%`, background: tier.bar, borderRadius: 8, transition: 'width 0.8s ease' }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Outcome Metrics Panel */}
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 28, padding: 28, boxShadow: '0 1px 8px rgba(0,0,0,0.04)', marginBottom: 32 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 24 }}>
            <div style={{ width: 4, height: 20, background: '#16a34a', borderRadius: 4 }} />
            <h3 style={{ fontSize: 12, fontWeight: 800, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.12em', margin: 0 }}>Intervention Outcome Metrics</h3>
          </div>

          {outcomes ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 16 }}>
              {[
                { label: 'Total Interventions', value: outcomes.total_interventions, color: '#6366f1', bg: '#eef2ff' },
                { label: 'Contacted', value: outcomes.contacted, color: '#0891b2', bg: '#ecfeff' },
                { label: 'Successful Renewals', value: outcomes.successful, color: '#16a34a', bg: '#f0fdf4' },
                { label: 'Churned', value: outcomes.failed, color: '#dc2626', bg: '#fef2f2' },
                { label: 'Pending Outcome', value: outcomes.pending, color: '#d97706', bg: '#fffbeb' },
                { label: 'Success Rate', value: `${outcomes.success_rate}%`, color: outcomes.success_rate >= 50 ? '#16a34a' : '#dc2626', bg: outcomes.success_rate >= 50 ? '#f0fdf4' : '#fef2f2' },
              ].map((metric, i) => (
                <div key={i} style={{ background: metric.bg, borderRadius: 20, padding: '16px 20px', textAlign: 'center' }}>
                  <p style={{ fontSize: 9, color: metric.color, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.12em', margin: '0 0 8px 0', opacity: 0.8 }}>{metric.label}</p>
                  <p style={{ fontSize: 28, fontWeight: 900, color: metric.color, margin: 0, letterSpacing: '-1px', lineHeight: 1 }}>{metric.value}</p>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: 32, color: '#94a3b8', fontWeight: 700, fontSize: 13 }}>
              No intervention data yet. Outcome metrics will appear here once CSMs start approving outreach.
            </div>
          )}
        </div>

        {/* Accounts table */}
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 28, padding: 28, boxShadow: '0 1px 8px rgba(0,0,0,0.04)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 4, height: 20, background: '#0891b2', borderRadius: 4 }} />
              <h3 style={{ fontSize: 12, fontWeight: 800, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.12em', margin: 0 }}>All Accounts — Team View</h3>
              <span style={{ marginLeft: 8, padding: '2px 10px', background: '#f1f5f9', borderRadius: 20, fontSize: 11, fontWeight: 800, color: '#64748b' }}>{filteredAccounts.length}</span>
            </div>
            <input
              type="text"
              placeholder="Search accounts, CSMs…"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              style={{ padding: '10px 16px', border: '1px solid #e2e8f0', borderRadius: 14, fontSize: 13, fontWeight: 500, color: '#334155', outline: 'none', width: 260, background: '#f8fafc' }}
            />
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #f1f5f9' }}>
                  {['Account', 'Account ID', 'CSM', 'Contract', 'Monthly', 'Risk Tier', 'Status'].map((h, i) => (
                    <th key={i} style={{ padding: '10px 14px', textAlign: 'left', fontSize: 10, fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.1em', whiteSpace: 'nowrap' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredAccounts.map((acc, i) => {
                  const tierStyle = getTierColor(acc.risk_tier);
                  return (
                    <tr key={i} style={{ borderBottom: '1px solid #f8fafc', transition: 'background 0.15s' }}
                      onMouseEnter={e => e.currentTarget.style.background = '#f8fafc'}
                      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                    >
                      <td style={{ padding: '14px', fontSize: 13, fontWeight: 700, color: '#1e293b' }}>{acc.name}</td>
                      <td style={{ padding: '14px', fontSize: 11, fontWeight: 600, color: '#94a3b8', fontFamily: 'monospace' }}>{acc.id}</td>
                      <td style={{ padding: '14px', fontSize: 13, fontWeight: 600, color: '#334155' }}>{acc.assigned_csm}</td>
                      <td style={{ padding: '14px', fontSize: 12, color: '#64748b', fontWeight: 600 }}>{acc.contract_type}</td>
                      <td style={{ padding: '14px', fontSize: 13, fontWeight: 700, color: '#0f172a', fontFamily: 'monospace' }}>${Number(acc.monthly_charges || 0).toFixed(0)}</td>
                      <td style={{ padding: '14px' }}>
                        <span style={{ padding: '3px 10px', background: tierStyle.bg, color: tierStyle.color, border: `1px solid ${tierStyle.border}`, borderRadius: 8, fontSize: 10, fontWeight: 900, letterSpacing: '0.06em' }}>
                          {acc.risk_tier || '—'}
                        </span>
                      </td>
                      <td style={{ padding: '14px' }}>
                        <span style={{
                          padding: '3px 10px', borderRadius: 8, fontSize: 10, fontWeight: 900, letterSpacing: '0.06em',
                          background: acc.status === 'Contacted' ? '#f0fdf4' : '#f8fafc',
                          color: acc.status === 'Contacted' ? '#16a34a' : '#64748b',
                          border: acc.status === 'Contacted' ? '1px solid #bbf7d0' : '1px solid #e2e8f0'
                        }}>
                          {acc.status || 'Active'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {filteredAccounts.length === 0 && (
              <div style={{ padding: 48, textAlign: 'center', color: '#94a3b8', fontWeight: 700, fontSize: 14 }}>No accounts match your search.</div>
            )}
          </div>
        </div>

        {/* Risk Engine Configuration Panel */}
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 28, padding: 28, boxShadow: '0 1px 8px rgba(0,0,0,0.04)', marginTop: 32 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 4, height: 20, background: '#7c3aed', borderRadius: 4 }} />
              <h3 style={{ fontSize: 12, fontWeight: 800, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.12em', margin: 0 }}>Risk Engine Configuration</h3>
            </div>
            <span style={{ fontSize: 11, color: '#94a3b8', fontWeight: 600 }}>Click any row to edit. Changes apply to all future risk calculations.</span>
          </div>

          {thresholds.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 32, color: '#94a3b8', fontWeight: 700, fontSize: 13 }}>
              No thresholds configured yet. Run <code style={{ background: '#f1f5f9', padding: '2px 8px', borderRadius: 6, fontFamily: 'monospace', fontSize: 12 }}>python seed_thresholds.py</code> to initialize.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 12 }}>
              {thresholds.map((t) => {
                const isEditing = editingThreshold === t.rule_name;
                const isSaved = thresholdSaved === t.rule_name;
                const isError = thresholdError === t.rule_name;
                return (
                  <div key={t.rule_name} style={{
                    border: `1.5px solid ${isEditing ? '#7c3aed' : isSaved ? '#16a34a' : isError ? '#dc2626' : '#e2e8f0'}`,
                    borderRadius: 18, padding: '16px 20px', background: isEditing ? '#faf5ff' : '#f8fafc',
                    transition: 'all 0.2s', cursor: 'pointer'
                  }}
                    onClick={() => !isEditing && setEditingThreshold(t.rule_name)}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                      <div>
                        <div style={{ fontSize: 12, fontWeight: 800, color: '#0f172a', marginBottom: 2 }}>{t.label}</div>
                        <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 600, lineHeight: 1.4 }}>{t.description}</div>
                      </div>
                      {isSaved && (
                        <span style={{ padding: '2px 10px', background: '#f0fdf4', color: '#16a34a', border: '1px solid #bbf7d0', borderRadius: 8, fontSize: 10, fontWeight: 900, whiteSpace: 'nowrap' }}>Saved ✓</span>
                      )}
                      {isError && (
                        <span style={{ padding: '2px 10px', background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca', borderRadius: 8, fontSize: 10, fontWeight: 900, whiteSpace: 'nowrap' }}>Error ✗</span>
                      )}
                    </div>

                    {isEditing ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10 }} onClick={e => e.stopPropagation()}>
                        <input
                          type="number"
                          value={thresholdValues[t.rule_name] ?? t.value}
                          min={t.min_value}
                          max={t.max_value}
                          step={t.unit === '%' || t.unit === 'points' ? 1 : 0.5}
                          onChange={e => setThresholdValues(prev => ({ ...prev, [t.rule_name]: e.target.value }))}
                          style={{ flex: 1, padding: '8px 12px', border: '1.5px solid #7c3aed', borderRadius: 10, fontSize: 14, fontWeight: 800, color: '#7c3aed', outline: 'none', background: '#fff', fontFamily: 'Inter, sans-serif' }}
                          autoFocus
                        />
                        <span style={{ fontSize: 11, color: '#7c3aed', fontWeight: 700 }}>{t.unit}</span>
                        <button
                          onClick={() => handleSaveThreshold(t.rule_name)}
                          style={{ padding: '8px 16px', background: '#7c3aed', color: '#fff', border: 'none', borderRadius: 10, fontSize: 12, fontWeight: 800, cursor: 'pointer', whiteSpace: 'nowrap' }}
                        >Save</button>
                        <button
                          onClick={() => { setEditingThreshold(null); setThresholdValues(prev => ({ ...prev, [t.rule_name]: t.value })); }}
                          style={{ padding: '8px 12px', background: '#f1f5f9', color: '#64748b', border: 'none', borderRadius: 10, fontSize: 12, fontWeight: 700, cursor: 'pointer' }}
                        >✕</button>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10 }}>
                        <span style={{ fontSize: 24, fontWeight: 900, color: '#7c3aed', letterSpacing: '-1px', lineHeight: 1 }}>{thresholdValues[t.rule_name] ?? t.value}</span>
                        <span style={{ fontSize: 12, color: '#94a3b8', fontWeight: 700 }}>{t.unit}</span>
                        <div style={{ marginLeft: 'auto', padding: '4px 12px', background: '#ede9fe', color: '#7c3aed', borderRadius: 8, fontSize: 10, fontWeight: 800 }}>Edit</div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ marginTop: 32, textAlign: 'center', fontSize: 11, color: '#cbd5e1', fontWeight: 600 }}>
          ChurnAlert AI — Admin Dashboard · {new Date().getFullYear()}
        </div>
      </div>
    </div>
  );
}
