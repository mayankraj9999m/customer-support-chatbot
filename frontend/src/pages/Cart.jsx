import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function Cart() {
  const [cart, setCart] = useState([]);
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  useEffect(() => {
    const savedCart = JSON.parse(localStorage.getItem('cart') || '[]');
    setCart(savedCart);
  }, []);

  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const handleCheckout = async () => {
    if (!token) {
      alert("Please log in to checkout.");
      navigate('/login');
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/orders/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          items: cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity
          }))
        })
      });

      if (response.ok) {
        localStorage.removeItem('cart');
        setCart([]);
        alert("Order placed successfully!");
        navigate('/orders');
      } else {
        const error = await response.json();
        alert(error.detail || "Checkout failed");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred during checkout");
    }
  };

  const removeItem = (id) => {
    const newCart = cart.filter(item => item.product_id !== id);
    setCart(newCart);
    localStorage.setItem('cart', JSON.stringify(newCart));
  };

  if (cart.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 24px' }}>
        <h2 className="heading-lg">Your cart is empty</h2>
        <Link to="/" className="btn btn-primary" style={{ marginTop: '24px' }}>Explore Products</Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '64px auto', padding: '0 24px' }}>
      <h1 className="heading-xl" style={{ marginBottom: '32px' }}>Shopping Cart</h1>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {cart.map(item => (
          <div key={item.product_id} style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '16px', backgroundColor: 'var(--surface-card)', borderRadius: 'var(--rounded-md)' }}>
            <img src={item.image_url} alt={item.name} style={{ width: '80px', height: '80px', objectFit: 'cover', borderRadius: 'var(--rounded-sm)' }} />
            <div style={{ flex: 1 }}>
              <h3 className="body-strong">{item.name}</h3>
              <p className="body-sm" style={{ color: 'var(--mute)' }}>Qty: {item.quantity}</p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p className="body-strong">${(item.price * item.quantity).toFixed(2)}</p>
              <button onClick={() => removeItem(item.product_id)} style={{ background: 'none', border: 'none', color: 'var(--error-deep)', cursor: 'pointer', marginTop: '8px' }} className="body-sm">Remove</button>
            </div>
          </div>
        ))}
      </div>
      
      <div style={{ marginTop: '48px', padding: '24px', backgroundColor: 'var(--surface-soft)', borderRadius: 'var(--rounded-lg)', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
        <p className="heading-md" style={{ marginBottom: '8px' }}>Total: ${total.toFixed(2)}</p>
        <p className="body-sm" style={{ color: 'var(--mute)', marginBottom: '24px' }}>Payment Method: Cash on Delivery</p>
        <button className="btn btn-primary" style={{ borderRadius: 'var(--rounded-full)', padding: '12px 32px' }} onClick={handleCheckout}>
          Checkout (COD)
        </button>
      </div>
    </div>
  );
}
