import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <Link to="/" className="footer-logo" lang="en">
          <svg width="20" height="20" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <circle cx="9.5" cy="9.5" r="6.5" stroke="#f472b6" strokeWidth="2" strokeLinecap="round"/>
            <line x1="14.2" y1="14.2" x2="20" y2="20" stroke="#f472b6" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <span className="logo-fake">Fake</span><span className="logo-scan">Scan</span>
        </Link>
        <nav className="footer-nav">
          <Link to="/privacy">プライバシーポリシー</Link>
          <Link to="/terms">利用規約</Link>
          <Link to="/contact">お問い合わせ</Link>
        </nav>
        <p className="footer-copy" lang="en">© 2026 FakeScan. All rights reserved.</p>
      </div>
    </footer>
  );
}
