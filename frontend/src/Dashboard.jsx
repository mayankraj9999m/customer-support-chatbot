import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import './Dashboard.css';

const HTTP_API_URL = 'http://localhost:8000/analytics';
const WS_API_URL = 'ws://localhost:8000/ws/analytics';

// Pinterest inspired charting colors
const COLORS = ['#e60023', '#33332e', '#62625b', '#91918c', '#c8c8c1'];

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(HTTP_API_URL);
      if (!response.ok) throw new Error("Network response was not ok");
      const result = await response.json();
      
      if (result.intent_distribution) {
          result.intent_distribution.sort((a, b) => b.value - a.value);
      }
      setData(result);
    } catch (error) {
      console.error("Error fetching analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchAnalytics();

    // Setup WebSocket for real-time updates
    const ws = new WebSocket(WS_API_URL);
    
    ws.onmessage = (event) => {
      if (event.data === "update_analytics") {
        console.log("WebSocket update received, fetching latest analytics...");
        fetchAnalytics();
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    return () => {
      ws.close();
    };
  }, []);

  if (loading && !data) {
    return (
      <div className="dashboard-container loading">
        <div className="spinner"></div>
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="dashboard-container error">
        <p>Failed to load analytics data.</p>
        <button onClick={fetchAnalytics}>Retry</button>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <h2>Real-Time Admin Dashboard</h2>
      
      <div className="kpi-cards">
        <div className="kpi-card">
          <h3>Total Conversations</h3>
          <p className="kpi-value">{data.total_messages}</p>
        </div>
        <div className="kpi-card">
          <h3>Average Confidence</h3>
          <p className="kpi-value">{(data.average_confidence * 100).toFixed(1)}%</p>
        </div>
        <div className="kpi-card">
          <h3>Unique Intents Discovered</h3>
          <p className="kpi-value">{data.intent_distribution.length}</p>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-box">
          <h3>Intent Distribution (Top 5)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.intent_distribution.slice(0, 5)}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {data.intent_distribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #dadad3', borderRadius: '16px', color: '#000' }}
                itemStyle={{ color: '#000' }}
              />
              <Legend iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-box">
          <h3>Intent Frequency</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={data.intent_distribution.slice(0, 5)}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e5e0" />
              <XAxis dataKey="name" stroke="#62625b" axisLine={false} tickLine={false} />
              <YAxis stroke="#62625b" axisLine={false} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #dadad3', borderRadius: '16px', color: '#000' }}
                cursor={{ fill: '#f6f6f3' }}
              />
              <Bar dataKey="value" fill="#e60023" radius={[16, 16, 16, 16]} barSize={40} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
