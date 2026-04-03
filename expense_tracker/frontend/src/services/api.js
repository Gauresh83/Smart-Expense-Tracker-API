import axios from 'axios';

const api = axios.create({ baseURL: '/api/v1' });

// Attach JWT on every request
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// Auto-refresh on 401
api.interceptors.response.use(
  r => r,
  async err => {
    const orig = err.config;
    if (err.response?.status === 401 && !orig._retry) {
      orig._retry = true;
      try {
        const refresh = localStorage.getItem('refresh');
        const { data } = await axios.post('/api/v1/auth/token/refresh/', { refresh });
        localStorage.setItem('access', data.access);
        orig.headers.Authorization = `Bearer ${data.access}`;
        return api(orig);
      } catch {
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(err);
  }
);

export default api;

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: d => api.post('/auth/register/', d),
  login:    d => api.post('/auth/login/', d),
  logout:   d => api.post('/auth/logout/', d),
  profile:  ()  => api.get('/users/me/'),
  updateProfile: d => api.patch('/users/me/', d),
  changePassword: d => api.put('/auth/password/change/', d),
};

// ── Expenses ──────────────────────────────────────────────────────────────────
export const expenseAPI = {
  list:   params => api.get('/expenses/', { params }),
  create: d      => api.post('/expenses/', d),
  update: (id,d) => api.patch(`/expenses/${id}/`, d),
  delete: id     => api.delete(`/expenses/${id}/`),
  export: d      => api.post('/expenses/export/', d),
};

// ── Categories ────────────────────────────────────────────────────────────────
export const categoryAPI = {
  list:   ()    => api.get('/categories/'),
  create: d     => api.post('/categories/', d),
  delete: id    => api.delete(`/categories/${id}/`),
};

// ── Budgets ───────────────────────────────────────────────────────────────────
export const budgetAPI = {
  list:   ()    => api.get('/budgets/'),
  create: d     => api.post('/budgets/', d),
  update: (id,d)=> api.patch(`/budgets/${id}/`, d),
  delete: id    => api.delete(`/budgets/${id}/`),
  status: id    => api.get(`/budgets/${id}/status/`),
};

// ── Analytics ─────────────────────────────────────────────────────────────────
export const analyticsAPI = {
  summary:     params => api.get('/analytics/summary/', { params }),
  byCategory:  params => api.get('/analytics/by-category/', { params }),
  trends:      params => api.get('/analytics/trends/', { params }),
  topExpenses: params => api.get('/analytics/top-expenses/', { params }),
};
