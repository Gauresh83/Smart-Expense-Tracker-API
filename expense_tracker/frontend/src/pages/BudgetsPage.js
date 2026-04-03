import React, { useEffect, useState } from 'react';
import { budgetAPI, categoryAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Plus, Trash2, AlertTriangle, CheckCircle } from 'lucide-react';

const EMPTY = { amount:'', period:'monthly', category:'', alert_threshold: 80 };

export default function BudgetsPage() {
  const [budgets,    setBudgets]    = useState([]);
  const [categories, setCategories] = useState([]);
  const [statuses,   setStatuses]   = useState({});
  const [showForm,   setShowForm]   = useState(false);
  const [form,       setForm]       = useState(EMPTY);

  const load = async () => {
    const [b, c] = await Promise.all([budgetAPI.list(), categoryAPI.list()]);
    setBudgets(b.data.results || []);
    setCategories(c.data.results || []);
    // load status for each budget
    const results = await Promise.all((b.data.results || []).map(bud => budgetAPI.status(bud.id)));
    const map = {};
    (b.data.results || []).forEach((bud, i) => { map[bud.id] = results[i].data; });
    setStatuses(map);
  };

  useEffect(() => { load(); }, []);

  const set = k => e => setForm({ ...form, [k]: e.target.value });

  const submit = async e => {
    e.preventDefault();
    try {
      const payload = { ...form };
      if (!payload.category) delete payload.category;
      await budgetAPI.create(payload);
      toast.success('Budget created');
      setForm(EMPTY); setShowForm(false); load();
    } catch { toast.error('Failed to create budget'); }
  };

  const del = async id => {
    if (!window.confirm('Delete budget?')) return;
    await budgetAPI.delete(id);
    toast.success('Deleted'); load();
  };

  const fmt = v => `$${parseFloat(v || 0).toFixed(2)}`;

  return (
    <div>
      <div className="page-header" style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', flexWrap:'wrap', gap:12, marginBottom:24 }}>
        <div>
          <h2>Budgets</h2>
          <p style={{ color:'var(--text2)' }}>Set spending limits and track utilization</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          <Plus size={16} /> New Budget
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom:24 }}>
          <h3 style={{ marginBottom:16, fontSize:15 }}>Create Budget</h3>
          <form onSubmit={submit} style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}>
            <div className="field"><label>Amount ($)</label>
              <input type="number" step="0.01" min="1" required value={form.amount} onChange={set('amount')} placeholder="500.00" />
            </div>
            <div className="field"><label>Period</label>
              <select value={form.period} onChange={set('period')}>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
            <div className="field"><label>Category (optional)</label>
              <select value={form.category} onChange={set('category')}>
                <option value="">All Categories</option>
                {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="field"><label>Alert at (%)</label>
              <input type="number" min="1" max="100" value={form.alert_threshold} onChange={set('alert_threshold')} />
            </div>
            <div style={{ gridColumn:'1/-1', display:'flex', gap:10 }}>
              <button className="btn-primary" type="submit">Save</button>
              <button className="btn-ghost" type="button" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {budgets.length === 0 ? (
        <div className="card" style={{ textAlign:'center', padding:'48px 0', color:'var(--text2)' }}>
          <Target size={40} style={{ marginBottom:12, opacity:.4 }} />
          <p>No budgets yet. Create one to start tracking!</p>
        </div>
      ) : (
        <div className="grid-2">
          {budgets.map(b => {
            const s = statuses[b.id];
            const pct = s?.utilization_pct || 0;
            const over = s?.is_over_budget;
            const color = over ? 'var(--red)' : pct >= b.alert_threshold ? 'var(--amber)' : 'var(--green)';
            return (
              <div className="card" key={b.id}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:16 }}>
                  <div>
                    <div style={{ fontWeight:600, fontSize:15 }}>
                      {categories.find(c => c.id === b.category)?.name || 'All Categories'}
                    </div>
                    <div style={{ color:'var(--text2)', fontSize:12, marginTop:2 }}>{b.period} budget</div>
                  </div>
                  <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                    {over
                      ? <AlertTriangle size={18} color="var(--red)" />
                      : <CheckCircle size={18} color="var(--green)" />}
                    <button className="btn-ghost" onClick={() => del(b.id)} style={{ padding:4, color:'var(--red)' }}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>

                {/* Progress bar */}
                <div style={{ background:'var(--bg3)', borderRadius:6, height:8, marginBottom:10, overflow:'hidden' }}>
                  <div style={{ width:`${Math.min(pct,100)}%`, height:'100%', background:color, borderRadius:6, transition:'width .4s' }} />
                </div>

                <div style={{ display:'flex', justifyContent:'space-between', fontSize:13 }}>
                  <span style={{ color:'var(--text2)' }}>Spent: <strong style={{ color:'var(--text)' }}>{fmt(s?.total_spent)}</strong></span>
                  <span style={{ color:'var(--text2)' }}>Limit: <strong style={{ color:'var(--text)' }}>{fmt(b.amount)}</strong></span>
                  <span style={{ color, fontWeight:700 }}>{pct.toFixed(1)}%</span>
                </div>

                {s && (
                  <div style={{ marginTop:8, fontSize:12, color:'var(--text2)' }}>
                    {s.period_start} → {s.period_end} &nbsp;·&nbsp; Remaining: <span style={{ color:'var(--green)', fontWeight:600 }}>{fmt(s.remaining)}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
