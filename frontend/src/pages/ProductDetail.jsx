import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/products/${id}`)
      .then(res => res.json())
      .then(data => setProduct(data))
      .catch(err => console.error(err));
  }, [id]);

  const handleAddToCart = () => {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    
    // Check if already in cart
    const existingIndex = cart.findIndex(item => item.product_id === product.id);
    if (existingIndex >= 0) {
      cart[existingIndex].quantity = Math.min(2, cart[existingIndex].quantity + quantity);
    } else {
      cart.push({
        product_id: product.id,
        name: product.name,
        price: product.price,
        image_url: product.image_url,
        quantity: quantity
      });
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    navigate('/cart');
  };

  if (!product) {
    return (
      <div style={{ maxWidth: '1024px', margin: '64px auto', padding: '0 24px', display: 'flex', gap: '48px', flexWrap: 'wrap' }}>
        <div style={{ flex: '1 1 400px' }}>
          <div className="skeleton" style={{ width: '100%', aspectRatio: '1/1', borderRadius: 'var(--rounded-lg)' }}></div>
        </div>
        <div style={{ flex: '1 1 400px' }}>
          <div className="skeleton skeleton-title" style={{ width: '80%', height: '40px' }}></div>
          <div className="skeleton skeleton-title" style={{ width: '30%', height: '24px', marginBottom: '32px' }}></div>
          
          <div className="skeleton skeleton-text" style={{ width: '100%' }}></div>
          <div className="skeleton skeleton-text" style={{ width: '100%' }}></div>
          <div className="skeleton skeleton-text" style={{ width: '80%', marginBottom: '48px' }}></div>
          
          <div className="skeleton" style={{ width: '100%', height: '48px', borderRadius: 'var(--rounded-full)' }}></div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1024px', margin: '64px auto', padding: '0 24px', display: 'flex', gap: '48px', flexWrap: 'wrap' }}>
      <div style={{ flex: '1 1 400px' }}>
        <img src={product.image_url} alt={product.name} style={{ width: '100%', borderRadius: 'var(--rounded-lg)' }} />
      </div>
      
      <div style={{ flex: '1 1 400px' }}>
        <h1 className="heading-xl">{product.name}</h1>
        <p className="heading-md" style={{ margin: '16px 0', color: 'var(--mute)' }}>${product.price.toFixed(2)}</p>
        
        <p className="body-md" style={{ marginBottom: '32px' }}>{product.description}</p>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
          <label className="body-strong">Quantity:</label>
          <select 
            className="input-field" 
            style={{ width: '80px', height: '40px' }} 
            value={quantity} 
            onChange={(e) => setQuantity(Number(e.target.value))}
          >
            <option value={1}>1</option>
            <option value={2}>2</option>
          </select>
          <span className="body-sm" style={{ color: 'var(--ash)' }}>Max 2 per order</span>
        </div>
        
        <button className="btn btn-primary" style={{ width: '100%', borderRadius: 'var(--rounded-full)', height: '48px' }} onClick={handleAddToCart}>
          Add to Cart
        </button>
      </div>
    </div>
  );
}
