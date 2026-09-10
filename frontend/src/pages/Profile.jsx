import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Profile() {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;

  const [name, setName] = useState(user?.name || '');
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  if (!token || !user) {
    navigate('/login');
    return null;
  }

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const payload = {};
      if (name !== user.name) payload.name = name;
      if (newPassword) {
        payload.old_password = oldPassword;
        payload.new_password = newPassword;
      }

      if (Object.keys(payload).length === 0) {
        return;
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/profile`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('user', JSON.stringify(data));
        setSuccess('Profile updated successfully!');
        setOldPassword('');
        setNewPassword('');
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to update profile');
      }
    } catch (err) {
      setError('An error occurred');
    }
  };

  return (
    <div style={{ maxWidth: '480px', margin: '64px auto', padding: '32px', backgroundColor: 'var(--canvas)', borderRadius: 'var(--rounded-lg)', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 className="heading-lg">Your Profile</h1>
      </div>

      {error && <div style={{ color: 'var(--error-deep)', backgroundColor: '#ffeeee', padding: '12px', borderRadius: 'var(--rounded-md)', marginBottom: '16px', fontSize: '14px' }}>{error}</div>}
      {success && <div style={{ color: 'var(--success-deep)', backgroundColor: '#eeffee', padding: '12px', borderRadius: 'var(--rounded-md)', marginBottom: '16px', fontSize: '14px' }}>{success}</div>}

      <form onSubmit={handleUpdateProfile} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <label className="body-strong" style={{ display: 'block', marginBottom: '8px' }}>Email ID</label>
          <input 
            type="email" 
            className="input-field" 
            value={user.email} 
            disabled 
            style={{ backgroundColor: 'var(--surface-soft)', color: 'var(--mute)', cursor: 'not-allowed' }}
          />
        </div>

        <div>
          <label className="body-strong" style={{ display: 'block', marginBottom: '8px' }}>Name</label>
          <input 
            type="text" 
            placeholder="Your name" 
            className="input-field" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
          />
        </div>

        <hr style={{ border: 'none', borderTop: '1px solid var(--hairline)', margin: '16px 0' }} />
        
        <h2 className="heading-md" style={{ marginBottom: '8px' }}>Change Password</h2>

        <div>
          <label className="body-strong" style={{ display: 'block', marginBottom: '8px' }}>Old Password</label>
          <input 
            type="password" 
            placeholder="Enter old password" 
            className="input-field" 
            value={oldPassword} 
            onChange={(e) => setOldPassword(e.target.value)} 
          />
        </div>

        <div>
          <label className="body-strong" style={{ display: 'block', marginBottom: '8px' }}>New Password</label>
          <input 
            type="password" 
            placeholder="Create a new password" 
            className="input-field" 
            value={newPassword} 
            onChange={(e) => setNewPassword(e.target.value)} 
          />
        </div>

        <button type="submit" className="btn btn-primary" style={{ borderRadius: 'var(--rounded-full)', height: '48px', marginTop: '16px' }}>
          Save Changes
        </button>
      </form>
    </div>
  );
}
