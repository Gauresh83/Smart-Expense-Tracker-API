import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { TrendingUp } from 'lucide-react';
import './AuthPage.css';

export default function RegisterPage() {
  const { register } = useAuth();
  const [form, setForm] = useState({ email:'', username:'', password:'', password2:'' });
  const [loading, setLoading] = useState(false);

  const set = k => e => setForm({ ...form, [k]: e.target.value });

  const submit = async e => {
    e.preventDefault();
    if (form.password !== form.password2) { toast.error('Passwords do not match'); return; }
    setLoading(true);
    try {
      await register(form);
      toast.success('Account created!');
    } catch (err) {
      const d = err.response?.data?.error?.detail;
      const msg = d ? Object.values(d)[0]?.[0] : 'Registration failed';
      toast.error(msg);
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <div className="auth-logo">
          <TrendingUp size={28} color="#6c63ff" />
          <h1>ExpenseIQ</h1>
        </div>
        <p className="auth-sub">Create your free account</p>
        <form onSubmit={submit} className="auth-form">
          {[
            { k:'email',     label:'Email',            type:'email',    ph:'you@example.com' },
            { k:'username',  label:'Username',          type:'text',     ph:'yourname' },
            { k:'password',  label:'Password',          type:'password', ph:'Min 8 characters' },
            { k:'password2', label:'Confirm Password',  type:'password', ph:'Repeat password' },
          ].map(({ k, label, type, ph }) => (
            <div className="field" key={k}>
              <label>{label}</label>
              <input type={type} placeholder={ph} required value={form[k]} onChange={set(k)} />
            </div>
          ))}
          <button className="btn-primary" type="submit" disabled={loading} style={{ width:'100%', justifyContent:'center' }}>
            {loading ? 'Creating…' : 'Create Account'}
          </button>
        </form>
        <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
      </div>
    </div>
  );
}
