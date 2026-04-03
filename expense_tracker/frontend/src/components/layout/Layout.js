import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard, Receipt, BarChart3, Target,
  User, LogOut, Menu, X, TrendingUp
} from 'lucide-react';
import './Layout.css';

const nav = [
  { to: '/',          icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/expenses',  icon: Receipt,         label: 'Expenses'  },
  { to: '/analytics', icon: BarChart3,        label: 'Analytics' },
  { to: '/budgets',   icon: Target,           label: 'Budgets'   },
  { to: '/profile',   icon: User,             label: 'Profile'   },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      {/* Mobile overlay */}
      {open && <div className="overlay" onClick={() => setOpen(false)} />}

      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="sidebar-logo">
          <TrendingUp size={22} color="#6c63ff" />
          <span>ExpenseIQ</span>
        </div>

        <nav className="sidebar-nav">
          {nav.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to} to={to} end={to === '/'}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setOpen(false)}
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="avatar">{user?.email?.[0]?.toUpperCase()}</div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 13 }}>{user?.username}</div>
              <div style={{ color: 'var(--text2)', fontSize: 11 }}>{user?.email}</div>
            </div>
          </div>
          <button className="btn-ghost" onClick={handleLogout} style={{ width:'100%', justifyContent:'flex-start', gap: 8, display:'flex', alignItems:'center', marginTop: 8 }}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <button className="btn-ghost menu-btn" onClick={() => setOpen(!open)}>
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </header>
        <div className="page-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
