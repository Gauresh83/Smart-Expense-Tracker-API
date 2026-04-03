import React, { useEffect, useState } from 'react';
import { analyticsAPI, expenseAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Bar, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { TrendingUp, TrendingDown, DollarSign, ShoppingBag } from 'lucide-react';
import './DashboardPage.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const COLORS = ['#6c63ff','#22c55e','#f59e0b','#ef4444','#3b82f6','#ec4899','#14b8a6','#a855f7'];

function StatCard({ label, value, icon: Icon, color, sub }) {
  return (
    <div className="stat-card card">
      <div className="stat-icon" style={{ background: color + '22', color }}>
        <Icon size={20} />
      </div>
      <div>
        <div className="stat-label">{label}</div>
        <div className="stat-value">{value}</div>
        {sub && <div className="stat-sub">{sub}</div>}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [summary, setSummary]     = useState(null);
  const [catData, setCatData]     = useState(null);
  const [trends,  setTrends]      = useState(null);
  const [recent,  setRecent]      = useState([]);

  useEffect(() => {
    analyticsAPI.summary({ period: 'month' }).then(r => setSummary(r.data));
    analyticsAPI.byCategory({}).then(r => setCatData(r.data));
    analyticsAPI.trends({ months: 6 }).then(r => setTrends(r.data));
    expenseAPI.list({ ordering: '-date', page_size: 5 }).then(r => setRecent(r.data.results || []));
  }, []);

  const fmt = v => `$${parseFloat(v || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

  const barData = trends ? {
    labels: trends.trends.map(t => t.month),
    datasets: [{
      label: 'Total Spent',
      data: trends.trends.map(t => parseFloat(t.total || 0)),
      backgroundColor: 'rgba(108,99,255,0.7)',
      borderRadius: 6,
    }]
  } : null;

  const doughnutData = catData ? {
    labels: catData.breakdown.map(b => b.category_name),
    datasets: [{
      data: catData.breakdown.map(b => parseFloat(b.total)),
      backgroundColor: COLORS,
      borderWidth: 0,
    }]
  } : null;

  const chartOpts = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#8b8fa8', font: { size: 12 } } } },
    scales: {
      x: { ticks: { color: '#8b8fa8' }, grid: { color: '#2e3350' } },
      y: { ticks: { color: '#8b8fa8' }, grid: { color: '#2e3350' } },
    }
  };

  const doughnutOpts = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { position: 'right', labels: { color: '#8b8fa8', font: { size: 12 }, padding: 16 } } },
    cutout: '65%',
  };

  return (
    <div className="dashboard">
      <div className="page-header">
        <h2>Good morning, {user?.username} 👋</h2>
        <p style={{ color: 'var(--text2)' }}>Here's your financial overview</p>
      </div>

      <div className="grid-4" style={{ marginBottom: 24 }}>
        <StatCard label="This Month"    value={fmt(summary?.total_spent)}   icon={DollarSign}    color="#6c63ff" sub={`${summary?.expense_count || 0} transactions`} />
        <StatCard label="Budget Used"   value={`${summary?.budget_utilization_pct || 0}%`} icon={TrendingUp} color="#22c55e" sub={`of ${fmt(summary?.budget_limit)}`} />
        <StatCard label="Avg Expense"   value={fmt(summary?.avg_expense)}   icon={ShoppingBag}   color="#f59e0b" />
        <StatCard label="Top Category"  value={summary?.top_category?.name || '—'} icon={TrendingDown} color="#ef4444" sub={fmt(summary?.top_category?.total)} />
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <h3 className="chart-title">Monthly Spending</h3>
          <div style={{ height: 240 }}>
            {barData ? <Bar data={barData} options={chartOpts} /> : <div className="loading-chart" />}
          </div>
        </div>
        <div className="card">
          <h3 className="chart-title">By Category</h3>
          <div style={{ height: 240 }}>
            {doughnutData ? <Doughnut data={doughnutData} options={doughnutOpts} /> : <div className="loading-chart" />}
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="chart-title" style={{ marginBottom: 16 }}>Recent Expenses</h3>
        {recent.length === 0 ? (
          <p style={{ color: 'var(--text2)', textAlign:'center', padding: '24px 0' }}>No expenses yet. Add your first expense!</p>
        ) : (
          <table className="expense-table">
            <thead><tr><th>Date</th><th>Description</th><th>Category</th><th>Amount</th></tr></thead>
            <tbody>
              {recent.map(e => (
                <tr key={e.id}>
                  <td style={{ color:'var(--text2)' }}>{e.date}</td>
                  <td>{e.description || '—'}</td>
                  <td><span className="badge" style={{ background: 'rgba(108,99,255,0.15)', color:'var(--primary-light)' }}>{e.category?.name || 'Uncategorized'}</span></td>
                  <td style={{ color:'var(--green)', fontWeight:600 }}>{fmt(e.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
