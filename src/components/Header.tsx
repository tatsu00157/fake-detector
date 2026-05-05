import React from 'react';
import { useAuth } from '../context/AuthContext';

export default function Header() {
  const { user, signOut } = useAuth();

  return (
    <header className="header">
      <div className="header-inner">
        <span className="header-logo">FakeDetector</span>
        <nav className="header-nav">
          {user ? (
            <>
              <span className="header-email">{user.email}</span>
              <button className="header-signout" onClick={signOut}>ログアウト</button>
            </>
          ) : (
            <a href="/login">ログイン</a>
          )}
        </nav>
      </div>
    </header>
  );
}
