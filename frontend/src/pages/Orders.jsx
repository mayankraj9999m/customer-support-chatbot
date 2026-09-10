import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!token) return;

    fetch(`${import.meta.env.VITE_API_URL}/orders/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setOrders(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [token]);

  if (!token) {
    return <div style={{ textAlign: 'center', padding: '100px 24px' }}>Please log in to view your orders.</div>;
  }

  if (loading) {
    return (
      <div style={{ maxWidth: '800px', margin: '64px auto', padding: '0 24px' }}>
        <div className="skeleton skeleton-title" style={{ width: '200px', marginBottom: '32px' }}></div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {[1, 2].map(i => (
            <div key={i} style={{ border: '1px solid var(--hairline)', borderRadius: 'var(--rounded-md)' }}>
              <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--hairline)' }}>
                <div className="skeleton skeleton-text" style={{ width: '150px' }}></div>
                <div className="skeleton skeleton-text" style={{ width: '100px' }}></div>
              </div>
              <div style={{ padding: '24px', display: 'flex', gap: '16px' }}>
                <div className="skeleton skeleton-img" style={{ width: '120px', height: '120px' }}></div>
                <div className="skeleton skeleton-img" style={{ width: '120px', height: '120px' }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '64px auto', padding: '0 24px' }}>
      <h1 className="heading-xl" style={{ marginBottom: '32px' }}>Order History</h1>
      
      {orders.length === 0 ? (
        <p className="body-md">You have no previous orders.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {orders.map(order => (
            <div key={order.id} style={{ border: '1px solid var(--hairline)', borderRadius: 'var(--rounded-md)', overflow: 'hidden' }}>
              <div style={{ backgroundColor: 'var(--surface-soft)', padding: '16px 24px', display: 'flex', flexWrap: 'wrap', gap: '16px', justifyContent: 'space-between', borderBottom: '1px solid var(--hairline)' }}>
                <div>
                  <p className="body-sm" style={{ color: 'var(--mute)' }}>Order ID: #{order.id}</p>
                  <p className="body-strong" style={{ marginTop: '4px' }}>Tracking: {order.tracking_number}</p>
                </div>
                <div style={{ textAlign: 'left' }}>
                  <p className="body-sm" style={{ color: 'var(--mute)' }}>Total</p>
                  <p className="body-strong">${order.total_amount.toFixed(2)}</p>
                </div>
              </div>
              
              <div style={{ padding: '24px', display: 'flex', gap: '16px', overflowX: 'auto' }}>
                {order.items.map(item => (
                  <Link key={item.product_id} to={`/product/${item.product_id}`} style={{ textDecoration: 'none', color: 'var(--ink)' }}>
                    <div style={{ width: '120px' }}>
                      <img src={item.product_image} alt={item.product_name} style={{ width: '120px', height: '120px', objectFit: 'cover', borderRadius: 'var(--rounded-sm)', marginBottom: '8px' }} />
                      <p className="body-sm-strong" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.product_name}</p>
                      <p className="body-sm" style={{ color: 'var(--mute)' }}>Qty: {item.quantity}</p>
                    </div>
                  </Link>
                ))}
              </div>
              
              <div style={{ backgroundColor: 'var(--surface-card)', padding: '12px 24px', borderTop: '1px solid var(--hairline)' }}>
                <span className="body-sm-strong">Status: </span>
                <span className={`body-sm ${order.status === 'Canceled' ? 'text-error' : ''}`} style={{ color: order.status === 'Canceled' ? 'var(--error-deep)' : 'var(--success-deep)' }}>
                  {order.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
