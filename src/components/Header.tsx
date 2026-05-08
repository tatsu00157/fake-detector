import React from 'react';
import { Link } from 'react-router-dom';

export default function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/" className="header-logo" lang="en" onClick={() => window.scrollTo(0, 0)}>
          <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <circle cx="9.5" cy="9.5" r="6.5" stroke="#f472b6" strokeWidth="2" strokeLinecap="round"/>
            <line x1="14.2" y1="14.2" x2="20" y2="20" stroke="#f472b6" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <span className="logo-fake">Fake</span><span className="logo-scan">Scan</span>
        </Link>
        <nav className="header-nav">
          <Link to="/" className="header-home-link" onClick={() => window.scrollTo(0, 0)}>ホーム</Link>
        </nav>
      </div>
    </header>
  );
}
