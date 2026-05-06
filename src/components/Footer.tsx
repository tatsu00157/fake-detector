import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <Link to="/" className="footer-logo" lang="en">
          <span className="logo-fake">Fake</span><span className="logo-scan">Scan</span>
        </Link>
        <nav className="footer-nav">
          <Link to="/privacy">プライバシーポリシー</Link>
          <Link to="/terms">利用規約</Link>
          <Link to="/contact">お問い合わせ</Link>
        </nav>
        <p className="footer-copy" lang="en">© 2025 FakeScan. All rights reserved.</p>
      </div>
    </footer>
  );
}
