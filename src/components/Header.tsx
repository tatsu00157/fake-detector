import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Header() {
  const { user, signOut } = useAuth();

  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/" className="header-logo" translate="no">
          <span className="logo-fake">Fake</span><span className="logo-scan">Scan</span>
        </Link>
        <nav className="header-nav">
          <Link to="/pricing" className="header-pricing">料金プラン</Link>
          {user ? (
            <>
              <span className="header-email">{user.email}</span>
              <button className="header-signout" onClick={signOut}>ログアウト</button>
            </>
          ) : (
            <>
              <Link to="/login" className="header-login">ログイン</Link>
              <Link to="/signup" className="header-signup">新規登録</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
