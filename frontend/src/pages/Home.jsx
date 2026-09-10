import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function Home() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/products/`)
      .then(res => res.json())
      .then(data => { setProducts(data); setIsLoading(false); })
      .catch(err => { console.error(err); setIsLoading(false); });
  }, []);

  return (
    <div>
      <div style={{ textAlign: 'center', padding: '64px 24px', backgroundColor: 'var(--surface-soft)' }}>
        <h1 className="display-xl">Create the life you love</h1>
        <p className="body-md" style={{ marginTop: '16px', maxWidth: '600px', marginInline: 'auto' }}>
          Discover our curated collection of premium products designed for everyday excellence.
        </p>
      </div>

      <div className="masonry-grid" style={{ marginTop: '32px' }}>
        {isLoading ? (
          Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="pin-item" style={{ padding: '12px' }}>
              <div className="skeleton skeleton-img" style={{ marginBottom: '12px', borderRadius: 'var(--rounded-md)' }}></div>
              <div className="skeleton skeleton-title"></div>
              <div className="skeleton skeleton-text" style={{ width: '40%' }}></div>
            </div>
          ))
        ) : (
          products.map(product => (
            <Link to={`/product/${product.id}`} key={product.id} className="pin-item" style={{ display: 'block', textDecoration: 'none' }}>
              <img src={product.image_url} alt={product.name} className="pin-image" />
              <div className="pin-overlay">
                <span className="btn btn-primary" style={{ borderRadius: 'var(--rounded-full)', padding: '8px 16px', fontSize: '14px' }}>
                  View
                </span>
              </div>
              <div style={{ padding: '12px' }}>
                <h3 className="body-strong" style={{ color: 'var(--ink)' }}>{product.name}</h3>
                <p className="body-sm" style={{ color: 'var(--mute)' }}>${product.price.toFixed(2)}</p>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
