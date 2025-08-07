import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/analysis', label: 'Analysis Details', icon: '🔍' },
    { path: '/events', label: 'Event Explorer', icon: '📅' },
  ];

  return (
    <header style={styles.header}>
      <div className="container" style={styles.container}>
        <div style={styles.brand}>
          <h1 style={styles.title}>
            🛢️ Brent Oil Change Point Analysis
          </h1>
          <p style={styles.subtitle}>
            Interactive Bayesian Analysis Dashboard
          </p>
        </div>
        
        <nav style={styles.nav}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                ...styles.navLink,
                ...(location.pathname === item.path ? styles.activeNavLink : {}),
              }}
            >
              <span style={styles.navIcon}>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
};

const styles = {
  header: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '20px 0',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  },
  container: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '20px',
  },
  brand: {
    flex: '1',
  },
  title: {
    fontSize: '1.8rem',
    fontWeight: '700',
    margin: '0 0 4px 0',
    color: 'white',
  },
  subtitle: {
    fontSize: '0.9rem',
    opacity: '0.9',
    margin: '0',
  },
  nav: {
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
  },
  navLink: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '10px 16px',
    borderRadius: '8px',
    textDecoration: 'none',
    color: 'white',
    fontSize: '0.9rem',
    fontWeight: '500',
    transition: 'all 0.2s ease',
    opacity: '0.8',
  },
  activeNavLink: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    opacity: '1',
  },
  navIcon: {
    fontSize: '1rem',
  },
};

// Add responsive styles
const mediaQuery = window.matchMedia('(max-width: 768px)');
if (mediaQuery.matches) {
  styles.container.flexDirection = 'column';
  styles.container.textAlign = 'center';
  styles.nav.flexWrap = 'wrap';
  styles.nav.justifyContent = 'center';
}

export default Header;
