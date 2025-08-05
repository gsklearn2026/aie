import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <h2>📊 Analytics Engine</h2>
      </div>
      <div className="nav-links">
        <Link 
          to="/dashboard" 
          className={location.pathname === '/dashboard' || location.pathname === '/' ? 'active' : ''}
        >
          Dashboard
        </Link>
        <Link 
          to="/user/demo-user" 
          className={location.pathname.includes('/user/') ? 'active' : ''}
        >
          User Analytics
        </Link>
        <Link 
          to="/topic/mathematics" 
          className={location.pathname.includes('/topic/') ? 'active' : ''}
        >
          Topic Analytics
        </Link>
      </div>
    </nav>
  );
};

export default Navigation;
