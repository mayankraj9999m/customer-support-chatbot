import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/');
        window.location.reload();
      } else {
        const data = await response.json();
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      setError('An error occurred');
    }
  };

  return (
    <div style={{ maxWidth: '480px', margin: '64px auto', padding: '32px', backgroundColor: 'var(--canvas)', borderRadius: 'var(--rounded-lg)', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '48px', height: '48px', backgroundColor: 'var(--primary)', color: 'var(--on-primary)', borderRadius: '50%', fontSize: '24px', fontWeight: 'bold', marginBottom: '16px' }}>P</div>
        <h1 className="heading-lg">Welcome to Pinterest E-Commerce</h1>
      </div>

      {error && <div style={{ color: 'var(--error-deep)', backgroundColor: '#ffeeee', padding: '12px', borderRadius: 'var(--rounded-md)', marginBottom: '16px', fontSize: '14px' }}>{error}</div>}

      <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <input 
          type="email" 
          placeholder="Email" 
          className="input-field" 
          value={email} 
          onChange={(e) => setEmail(e.target.value)} 
          required 
        />
        <input 
          type="password" 
          placeholder="Password" 
          className="input-field" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
          required 
        />
        <button type="submit" className="btn btn-primary" style={{ borderRadius: 'var(--rounded-full)', height: '48px', marginTop: '8px' }}>
          Log in
        </button>
      </form>

      <div style={{ textAlign: 'center', marginTop: '24px' }}>
        <Link to="/register" style={{ color: 'var(--ink)', fontWeight: 600, fontSize: '14px', textDecoration: 'none' }}>Not on Pinterest E-Commerce yet? Sign up</Link>
      </div>
    </div>
  );
}
