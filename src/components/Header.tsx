import React from 'react';

export default function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <span className="header-logo">FakeDetector</span>
        <nav className="header-nav">
          <a href="/">解析</a>
          <a href="/pricing">料金プラン</a>
        </nav>
      </div>
    </header>
  );
}
