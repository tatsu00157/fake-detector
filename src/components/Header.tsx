import React from 'react';
import { Link } from 'react-router-dom';

export default function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/" className="header-logo" lang="en">
          <span className="logo-fake">Fake</span><span className="logo-scan">Scan</span>
        </Link>
      </div>
    </header>
  );
}
