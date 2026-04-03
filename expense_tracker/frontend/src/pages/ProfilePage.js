import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authAPI, categoryAPI } from '../services/api';
import toast from 'react-hot-toast';
import { User, Lock, Tag, Plus, Trash2 } from 'lucide-react';
import { useEffect } from 'react';

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [profile, setProfile] = useState({ username: user?.username || '', currency: user?.currency || 'USD', timezone: user?.timezone || 'UTC', monthly_budget: user?.monthly_budget || '' });
  const [passwords, setPasswords] = useState({ old_password:'', new_password:'' });
  const [categories, setCategories] = useState([]);
  const [newCat, setNewCat] = useState({ name:'', color:'#6c63ff' });

  useEffect(() => { categoryAPI.list().then(r => setCategories(r.data.results || [])); }, []);

  const saveProfile = async e => {
    e.preventDefault();
    try {
      await authAPI.updateProfile(profile);
      await refreshUser();
      toast.success('Profile updated');
    } catch { toast.error('Failed to update profile'); }
  };

  const changePassword = async e => {
    e.preventDefault();
    try {
      await authAPI.changePassword(passwords);
      toast.success('Password changed');
      setPasswords({ old_password:'', new_password:'' });
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed');
    }
  };

  const addCategory = async e => {
    e.preventDefault();
    try {
      await categoryAPI.create(newCat);
      toast.success('Category created');
      setNewCat({ name:'', color:'#6c63ff' });
      categoryAPI.list().then(r => setCategories(r.data.results || []));
    } catch { toast.error('Failed'); }
  };

  const delCategory = async id => {
    await categoryAPI.delete(id);
    setCategories(categories.filter(c => c.id !== id));
    toast.success('Deleted');
  };

  const section = (icon, title, children) => (
    <div className="card" style={{ marginBottom:20 }}>
      <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:20 }}>
        <div style={{ background:'rgba(108,99,255,.15)', color:'var(--primary-light)', width:36, height:36, borderRadius:9, display:'flex', alignItems:'center', justifyContent:'center' }}>
          {icon}
        </div>
        <h3 style={{ fontSize:15, fontWeight:600 }}>{title}</h3>
      </div>
      {children}
    </div>
  );

  return (
    <div style={{ maxWidth:680 }}>
      <div className="page-header" style={{ marginBottom:24 }}>
        <h2>Profile & Settings</h2>
        <p style={{ color:'var(--text2)' }}>Manage your account and preferences</p>
      </div>

      {section(<User size={18}/>, 'Personal Information',
        <form onSubmit={saveProfile} style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}>
          <div className="field"><label>Username</label>
            <input value={profile.username} onChange={e => setProfile({...profile, username:e.target.value})} />
          </div>
          <div className="field"><label>Currency</label>
            <select value={profile.currency} onChange={e => setProfile({...profile, currency:e.target.value})}>
              {['USD','EUR','GBP','INR','JPY','AUD','CAD'].map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="field"><label>Timezone</label>
            <select value={profile.timezone} onChange={e => setProfile({...profile, timezone:e.target.value})}>
              {['UTC','US/Eastern','US/Pacific','Europe/London','Asia/Kolkata','Asia/Tokyo'].map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="field"><label>Monthly Budget ($)</label>
            <input type="number" step="0.01" value={profile.monthly_budget} onChange={e => setProfile({...profile, monthly_budget:e.target.value})} placeholder="e.g. 2000" />
          </div>
          <div style={{ gridColumn:'1/-1' }}>
            <button className="btn-primary" type="submit">Save Changes</button>
          </div>
        </form>
      )}

      {section(<Lock size={18}/>, 'Change Password',
        <form onSubmit={changePassword} style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}>
          <div className="field"><label>Current Password</label>
            <input type="password" value={passwords.old_password} onChange={e => setPasswords({...passwords, old_password:e.target.value})} required />
          </div>
          <div className="field"><label>New Password</label>
            <input type="password" value={passwords.new_password} onChange={e => setPasswords({...passwords, new_password:e.target.value})} required />
          </div>
          <div style={{ gridColumn:'1/-1' }}>
            <button className="btn-primary" type="submit">Update Password</button>
          </div>
        </form>
      )}

      {section(<Tag size={18}/>, 'Categories',
        <>
          <form onSubmit={addCategory} style={{ display:'flex', gap:12, marginBottom:16, flexWrap:'wrap' }}>
            <input placeholder="Category name" value={newCat.name} onChange={e => setNewCat({...newCat, name:e.target.value})} required style={{ flex:1, minWidth:140 }} />
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <label style={{ fontSize:12, color:'var(--text2)' }}>Color</label>
              <input type="color" value={newCat.color} onChange={e => setNewCat({...newCat, color:e.target.value})} style={{ width:40, height:36, padding:2, cursor:'pointer', background:'var(--bg3)' }} />
            </div>
            <button className="btn-primary" type="submit"><Plus size={14}/> Add</button>
          </form>
          <div style={{ display:'flex', flexWrap:'wrap', gap:10 }}>
            {categories.map(c => (
              <div key={c.id} style={{ display:'flex', alignItems:'center', gap:8, background:'var(--bg3)', padding:'6px 12px', borderRadius:20, fontSize:13 }}>
                <span style={{ width:10, height:10, borderRadius:'50%', background:c.color, flexShrink:0 }} />
                {c.name}
                <button onClick={() => delCategory(c.id)} style={{ background:'none', color:'var(--text2)', cursor:'pointer', display:'flex', padding:0 }}>
                  <Trash2 size={12}/>
                </button>
              </div>
            ))}
            {categories.length === 0 && <p style={{ color:'var(--text2)', fontSize:13 }}>No categories yet</p>}
          </div>
        </>
      )}
    </div>
  );
}
