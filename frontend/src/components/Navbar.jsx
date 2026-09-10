import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, ShoppingCart, User as UserIcon, LogOut } from 'lucide-react';
import './Navbar.css';

export default function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const user = JSON.parse(localStorage.getItem('user') || 'null');

  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const searchRef = useRef(null);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/products/`)
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    if (!isDropdownOpen) setIsDropdownOpen(true);
  };

  const filteredProducts = searchQuery.trim() === '' 
    ? [] 
    : products.filter(p => 
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
        p.description.toLowerCase().includes(searchQuery.toLowerCase())
      );

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <nav className="primary-nav">
      <div className="nav-left">
        <Link to="/" className="brand-logo">
          <div className="p-logo">P</div>
          <span className="brand-text">E-Commerce</span>
        </Link>
        <Link to="/" className="nav-link nav-link-active">Explore</Link>
      </div>

      <div className="nav-center">
        <div className="search-container" ref={searchRef}>
          <div className="search-bar">
            <Search size={20} className="search-icon" />
            <input 
              type="text" 
              placeholder="Search for ideas, fashion, tech..." 
              value={searchQuery}
              onChange={handleSearchChange}
              onFocus={() => setIsDropdownOpen(true)}
            />
          </div>
          
          {isDropdownOpen && searchQuery.trim() !== '' && (
            <div className="search-dropdown">
              {filteredProducts.length > 0 ? (
                filteredProducts.map(product => (
                  <Link 
                    key={product.id} 
                    to={`/product/${product.id}`} 
                    className="search-result-item"
                    onClick={() => {
                      setIsDropdownOpen(false);
                      setSearchQuery('');
                    }}
                  >
                    <img src={product.image_url} alt={product.name} className="search-result-img" />
                    <div className="search-result-info">
                      <h4>{product.name}</h4>
                      <p>${product.price.toFixed(2)}</p>
                    </div>
                  </Link>
                ))
              ) : (
                <div className="search-no-results">
                  No products found matching "{searchQuery}"
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="nav-right">
        <Link to="/analytics" className="nav-link">Analytics</Link>
        {token ? (
          <>
            <Link to="/profile" className="nav-link">Profile</Link>
            <Link to="/orders" className="nav-link">Orders</Link>
            <Link to="/cart" className="icon-btn">
              <ShoppingCart size={24} />
            </Link>
            <button onClick={handleLogout} className="icon-btn" style={{ color: 'var(--primary)', border: 'none', background: 'transparent', cursor: 'pointer' }} title="Log out">
              <LogOut size={24} />
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="btn btn-secondary">Log in</Link>
            <Link to="/register" className="btn btn-primary">Sign up</Link>
          </>
        )}
      </div>
    </nav>
  );
}
