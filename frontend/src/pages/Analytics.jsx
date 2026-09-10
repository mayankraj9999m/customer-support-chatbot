import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/analytics`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch analytics');
        return res.json();
      })
      .then(data => setAnalytics(data))
      .catch(err => setError(err.message));
  }, []);

  return (
    <div style={{ maxWidth: '1024px', margin: '64px auto', padding: '0 24px' }}>
      <h1 className="heading-xl" style={{ marginBottom: '32px' }}>Analytics Dashboard</h1>
      
      {error && <p style={{ color: 'var(--error-deep)' }}>{error}</p>}
      
      {!analytics ? (
        <div className="card" style={{ padding: '24px', marginBottom: '32px' }}>
          <div className="skeleton skeleton-title" style={{ width: '200px', marginBottom: '24px' }}></div>
          <div className="skeleton" style={{ width: '100%', height: '300px', borderRadius: 'var(--rounded-md)' }}></div>
          <div style={{ display: 'flex', gap: '24px', marginTop: '24px', paddingTop: '24px', borderTop: '1px solid var(--hairline)' }}>
            <div className="skeleton skeleton-text" style={{ width: '120px', height: '40px' }}></div>
            <div className="skeleton skeleton-text" style={{ width: '120px', height: '40px' }}></div>
          </div>
        </div>
      ) : (
        <div className="card" style={{ padding: '24px', marginBottom: '32px' }}>
          <h2 className="heading-md" style={{ marginBottom: '24px' }}>Intent Analytics</h2>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.intent_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: 'var(--mute)' }} tickMargin={10} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 12, fill: 'var(--mute)' }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: 'var(--surface-soft)' }} contentStyle={{ borderRadius: 'var(--rounded-sm)', border: '1px solid var(--hairline)' }} />
                <Bar dataKey="value" fill="var(--primary)" radius={[4, 4, 0, 0]} name="Queries" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '24px', marginTop: '24px', paddingTop: '24px', borderTop: '1px solid var(--hairline)' }}>
            <div style={{ flex: '1 1 120px' }}>
              <p className="body-sm" style={{ color: 'var(--mute)' }}>Total Messages</p>
              <p className="heading-lg">{analytics.total_messages}</p>
            </div>
            <div style={{ flex: '1 1 120px' }}>
              <p className="body-sm" style={{ color: 'var(--mute)' }}>Avg. Confidence</p>
              <p className="heading-lg">{(analytics.average_confidence * 100).toFixed(1)}%</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
