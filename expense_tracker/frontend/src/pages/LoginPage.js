import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { TrendingUp, Mail, Lock } from 'lucide-react';
import './AuthPage.css';

export default function LoginPage() {
  const { login } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const submit = async e => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form.email, form.password);
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <div className="auth-logo">
          <TrendingUp size={28} color="#6c63ff" />
          <h1>ExpenseIQ</h1>
        </div>
        <p className="auth-sub">Sign in to your account</p>

        <form onSubmit={submit} className="auth-form">
          <div className="field">
            <label>Email</label>
            <div className="input-icon">
              <Mail size={16} />
              <input type="email" placeholder="you@example.com" required
                value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
            </div>
          </div>
          <div className="field">
            <label>Password</label>
            <div className="input-icon">
              <Lock size={16} />
              <input type="password" placeholder="••••••••" required
                value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
            </div>
          </div>
          <button className="btn-primary" type="submit" disabled={loading} style={{ width:'100%', justifyContent:'center' }}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <p className="auth-switch">Don't have an account? <Link to="/register">Register</Link></p>
      </div>
    </div>
  );
}
