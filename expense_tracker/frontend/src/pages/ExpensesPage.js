import React, { useEffect, useState, useCallback } from 'react';
import { expenseAPI, categoryAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Plus, Trash2, Search, Filter, Download } from 'lucide-react';
import './ExpensesPage.css';

const EMPTY = { amount:'', currency:'USD', description:'', date: new Date().toISOString().split('T')[0], category_id:'', recurrence:'none' };

export default function ExpensesPage() {
  const [expenses,   setExpenses]   = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [showForm,   setShowForm]   = useState(false);
  const [form,       setForm]       = useState(EMPTY);
  const [filters,    setFilters]    = useState({ search:'', category:'', date_from:'', date_to:'' });
  const [next,       setNext]       = useState(null);

  const load = useCallback(async (params = {}) => {
    setLoading(true);
    try {
      const r = await expenseAPI.list({ ...filters, ...params, page_size: 20 });
      setExpenses(r.data.results || []);
      setNext(r.data.next);
    } finally { setLoading(false); }
  }, [filters]);

  useEffect(() => { categoryAPI.list().then(r => setCategories(r.data.results || [])); }, []);
  useEffect(() => { load(); }, [load]);

  const set = k => e => setForm({ ...form, [k]: e.target.value });

  const submit = async e => {
    e.preventDefault();
    try {
      const payload = { ...form };
      if (!payload.category_id) delete payload.category_id;
      await expenseAPI.create(payload);
      toast.success('Expense added');
      setForm(EMPTY); setShowForm(false); load();
    } catch { toast.error('Failed to add expense'); }
  };

  const del = async id => {
    if (!window.confirm('Delete this expense?')) return;
    await expenseAPI.delete(id);
    toast.success('Deleted');
    load();
  };

  const exportCSV = async () => {
    await expenseAPI.export({ format:'csv', filters });
    toast.success('Export started — check your email');
  };

  const fmt = v => `$${parseFloat(v).toFixed(2)}`;

  return (
    <div>
      <div className="page-header" style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', flexWrap:'wrap', gap:12 }}>
        <div>
          <h2>Expenses</h2>
          <p style={{ color:'var(--text2)' }}>Manage and track all your expenses</p>
        </div>
        <div style={{ display:'flex', gap:10 }}>
          <button className="btn-ghost" onClick={exportCSV} style={{ display:'flex', alignItems:'center', gap:6 }}>
            <Download size={16} /> Export
          </button>
          <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
            <Plus size={16} /> Add Expense
          </button>
        </div>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom:16, fontSize:15 }}>New Expense</h3>
          <form onSubmit={submit} className="expense-form">
            <div className="field"><label>Amount</label>
              <input type="number" step="0.01" min="0.01" required value={form.amount} onChange={set('amount')} placeholder="0.00" />
            </div>
            <div className="field"><label>Date</label>
              <input type="date" required value={form.date} onChange={set('date')} />
            </div>
            <div className="field"><label>Category</label>
              <select value={form.category_id} onChange={set('category_id')}>
                <option value="">Uncategorized</option>
                {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="field"><label>Recurrence</label>
              <select value={form.recurrence} onChange={set('recurrence')}>
                {['none','daily','weekly','monthly'].map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div className="field" style={{ gridColumn:'1/-1' }}><label>Description</label>
              <input value={form.description} onChange={set('description')} placeholder="What was this for?" />
            </div>
            <div style={{ gridColumn:'1/-1', display:'flex', gap:10 }}>
              <button className="btn-primary" type="submit">Save</button>
              <button className="btn-ghost" type="button" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="filters-row">
          <div style={{ position:'relative', flex:1 }}>
            <Search size={14} style={{ position:'absolute', left:10, top:'50%', transform:'translateY(-50%)', color:'var(--text2)' }} />
            <input placeholder="Search expenses…" style={{ paddingLeft:32 }}
              value={filters.search} onChange={e => setFilters({...filters, search: e.target.value})} />
          </div>
          <select value={filters.category} onChange={e => setFilters({...filters, category: e.target.value})} style={{ width:160 }}>
            <option value="">All Categories</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <input type="date" value={filters.date_from} onChange={e => setFilters({...filters, date_from: e.target.value})} style={{ width:150 }} />
          <input type="date" value={filters.date_to}   onChange={e => setFilters({...filters, date_to: e.target.value})} style={{ width:150 }} />
          <button className="btn-primary" onClick={() => load()} style={{ whiteSpace:'nowrap' }}>
            <Filter size={14} /> Apply
          </button>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ textAlign:'center', padding:'40px 0', color:'var(--text2)' }}>Loading…</div>
        ) : expenses.length === 0 ? (
          <div style={{ textAlign:'center', padding:'40px 0', color:'var(--text2)' }}>No expenses found.</div>
        ) : (
          <table className="expense-table">
            <thead><tr><th>Date</th><th>Description</th><th>Category</th><th>Recurrence</th><th>Amount</th><th></th></tr></thead>
            <tbody>
              {expenses.map(e => (
                <tr key={e.id}>
                  <td style={{ color:'var(--text2)', whiteSpace:'nowrap' }}>{e.date}</td>
                  <td>{e.description || '—'}</td>
                  <td><span className="badge" style={{ background:'rgba(108,99,255,0.15)', color:'var(--primary-light)' }}>{e.category?.name || 'Uncategorized'}</span></td>
                  <td style={{ color:'var(--text2)' }}>{e.recurrence}</td>
                  <td style={{ color:'var(--green)', fontWeight:700 }}>{fmt(e.amount)}</td>
                  <td><button className="btn-ghost" onClick={() => del(e.id)} style={{ padding:'6px', color:'var(--red)' }}><Trash2 size={14}/></button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
