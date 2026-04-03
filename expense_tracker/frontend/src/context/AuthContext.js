import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access');
    if (token) {
      authAPI.profile()
        .then(r => setUser(r.data))
        .catch(() => localStorage.clear())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const { data } = await authAPI.login({ email, password });
    localStorage.setItem('access',  data.access);
    localStorage.setItem('refresh', data.refresh);
    const profile = await authAPI.profile();
    setUser(profile.data);
  };

  const register = async (payload) => {
    await authAPI.register(payload);
    await login(payload.email, payload.password);
  };

  const logout = async () => {
    try { await authAPI.logout({ refresh: localStorage.getItem('refresh') }); } catch {}
    localStorage.clear();
    setUser(null);
  };

  const refreshUser = async () => {
    const profile = await authAPI.profile();
    setUser(profile.data);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}
