import React from 'react';
import './AppHeader.css';

const TrainIcon: React.FC = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <rect x="4" y="3" width="16" height="13" rx="3" fill="currentColor" />
    <rect x="6" y="6" width="5" height="4" rx="1" fill="white" />
    <rect x="13" y="6" width="5" height="4" rx="1" fill="white" />
    <path d="M4 16l-2 4h20l-2-4" fill="currentColor" />
    <circle cx="8" cy="19" r="1.5" fill="white" />
    <circle cx="16" cy="19" r="1.5" fill="white" />
  </svg>
);

interface AppHeaderProps {
  onMenuToggle: () => void;
  sidebarOpen: boolean;
}

const AppHeader: React.FC<AppHeaderProps> = ({ onMenuToggle, sidebarOpen }) => (
  <header className="app-header">
    <div className="app-header__inner">
      <div className="app-header__brand">
        <button
          className="app-header__menu-btn"
          onClick={onMenuToggle}
          aria-label={sidebarOpen ? 'Close filters' : 'Open filters'}
          aria-expanded={sidebarOpen}
        >
          <MenuIcon open={sidebarOpen} />
        </button>
        <span className="app-header__logo-mark">
          <TrainIcon />
        </span>
        <div className="app-header__title-group">
          <span className="app-header__title">VIA Rail</span>
          <span className="app-header__subtitle">Performance Dashboard</span>
        </div>
      </div>

      <nav className="app-header__tabs" aria-label="Main tabs">
        <a href="/" className="app-header__tab app-header__tab--active">
          Performance
        </a>
        <a href="/map" className="app-header__tab">
          Live Map
        </a>
      </nav>
    </div>
  </header>
);

const MenuIcon: React.FC<{ open: boolean }> = ({ open }) => (
  <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true">
    {open ? (
      <>
        <line x1="4" y1="4" x2="18" y2="18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <line x1="18" y1="4" x2="4" y2="18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </>
    ) : (
      <>
        <line x1="3" y1="6" x2="19" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <line x1="3" y1="11" x2="19" y2="11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <line x1="3" y1="16" x2="19" y2="16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </>
    )}
  </svg>
);

export default AppHeader;
