import React, { useEffect, useState } from 'react';
import { analyticsAPI } from '../services/api';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS, ArcElement, Tooltip, Legend,
  CategoryScale, LinearScale, BarElement,
  PointElement, LineElement, Filler
} from 'chart.js';
import './AnalyticsPage.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler);

const COLORS = ['#6c63ff','#22c55e','#f59e0b','#ef4444','#3b82f6','#ec4899','#14b8a6','#a855f7'];
const fmt = v => `$${parseFloat(v||0).toFixed(2)}`;

const baseOpts = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { labels: { color: '#8b8fa8', font: { size: 12 } } } },
  scales: {
    x: { ticks: { color:'#8b8fa8' }, grid: { color:'#2e3350' } },
    y: { ticks: { color:'#8b8fa8', callback: v => `$${v}` }, grid: { color:'#2e3350' } },
  }
};

export default function AnalyticsPage() {
  const [period,  setPeriod]  = useState('month');
  const [months,  setMonths]  = useState(6);
  const [summary, setSummary] = useState(null);
  const [catData, setCatData] = useState(null);
  const [trends,  setTrends]  = useState(null);
  const [top,     setTop]     = useState([]);

  useEffect(() => {
    analyticsAPI.summary({ period }).then(r => setSummary(r.data));
    analyticsAPI.byCategory({}).then(r => setCatData(r.data));
  }, [period]);

  useEffect(() => {
    analyticsAPI.trends({ months }).then(r => setTrends(r.data));
    analyticsAPI.topExpenses({ limit: 5, period }).then(r => setTop(r.data.expenses || []));
  }, [months, period]);

  const lineData = trends ? {
    labels: trends.trends.map(t => t.month),
    datasets: [{
      label: 'Monthly Spend',
      data: trends.trends.map(t => parseFloat(t.total || 0)),
      borderColor: '#6c63ff',
      backgroundColor: 'rgba(108,99,255,0.1)',
      fill: true, tension: 0.4,
      pointBackgroundColor: '#6c63ff',
    }]
  } : null;

  const barData = catData ? {
    labels: catData.breakdown.map(b => b.category_name),
    datasets: [{
      label: 'Spending',
      data: catData.breakdown.map(b => parseFloat(b.total)),
      backgroundColor: COLORS,
      borderRadius: 6,
    }]
  } : null;

  const doughnutData = catData ? {
    labels: catData.breakdown.map(b => b.category_name),
    datasets: [{ data: catData.breakdown.map(b => parseFloat(b.total)), backgroundColor: COLORS, borderWidth: 0 }]
  } : null;

  const dOpts = { responsive:true, maintainAspectRatio:false, cutout:'65%',
    plugins: { legend: { position:'right', labels: { color:'#8b8fa8', font:{size:12}, padding:14 } } } };

  return (
    <div>
      <div className="page-header" style={{ marginBottom:24 }}>
        <h2>Analytics</h2>
        <p style={{ color:'var(--text2)' }}>Deep insights into your spending habits</p>
      </div>

      {/* Controls */}
      <div className="card" style={{ marginBottom:24, display:'flex', gap:16, flexWrap:'wrap', alignItems:'center' }}>
        <div>
          <label style={{ color:'var(--text2)', fontSize:12, marginRight:8 }}>Period</label>
          {['week','month','year'].map(p => (
            <button key={p} onClick={() => setPeriod(p)}
              className={period===p ? 'btn-primary' : 'btn-ghost'}
              style={{ marginRight:6, padding:'6px 14px', fontSize:13 }}>
              {p.charAt(0).toUpperCase()+p.slice(1)}
            </button>
          ))}
        </div>
        <div>
          <label style={{ color:'var(--text2)', fontSize:12, marginRight:8 }}>Trend months</label>
          {[3,6,12].map(m => (
            <button key={m} onClick={() => setMonths(m)}
              className={months===m ? 'btn-primary' : 'btn-ghost'}
              style={{ marginRight:6, padding:'6px 14px', fontSize:13 }}>
              {m}m
            </button>
          ))}
        </div>
      </div>

      {/* Summary row */}
      {summary && (
        <div className="grid-3" style={{ marginBottom:24 }}>
          {[
            { label:'Total Spent',    val: fmt(summary.total_spent) },
            { label:'Transactions',   val: summary.expense_count },
            { label:'Avg per tx',     val: fmt(summary.avg_expense) },
          ].map(({ label, val }) => (
            <div className="card" key={label} style={{ textAlign:'center' }}>
              <div style={{ color:'var(--text2)', fontSize:12, marginBottom:6 }}>{label}</div>
              <div style={{ fontSize:24, fontWeight:700 }}>{val}</div>
            </div>
          ))}
        </div>
      )}

      {/* Charts */}
      <div className="card" style={{ marginBottom:24 }}>
        <h3 className="chart-title">Spending Trend</h3>
        <div style={{ height:260 }}>
          {lineData ? <Line data={lineData} options={baseOpts} /> : <div className="loading-chart" />}
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom:24 }}>
        <div className="card">
          <h3 className="chart-title">Spend by Category (Bar)</h3>
          <div style={{ height:240 }}>
            {barData ? <Bar data={barData} options={{ ...baseOpts, plugins:{ legend:{ display:false } } }} /> : <div className="loading-chart" />}
          </div>
        </div>
        <div className="card">
          <h3 className="chart-title">Category Distribution</h3>
          <div style={{ height:240 }}>
            {doughnutData ? <Doughnut data={doughnutData} options={dOpts} /> : <div className="loading-chart" />}
          </div>
        </div>
      </div>

      {/* Top expenses */}
      <div className="card">
        <h3 className="chart-title" style={{ marginBottom:16 }}>Top Expenses This {period}</h3>
        {top.length === 0 ? (
          <p style={{ color:'var(--text2)', padding:'20px 0' }}>No data</p>
        ) : (
          <div className="top-list">
            {top.map((e, i) => (
              <div key={e.id} className="top-item">
                <span className="rank">#{i+1}</span>
                <div style={{ flex:1 }}>
                  <div>{e.description || 'Expense'}</div>
                  <div style={{ color:'var(--text2)', fontSize:12 }}>{e.category?.name || 'Uncategorized'} · {e.date}</div>
                </div>
                <span style={{ fontWeight:700, color:'var(--green)' }}>{fmt(e.amount)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
