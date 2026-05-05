import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { useAuth } from '../context/AuthContext';

const ERROR_MAP: Record<string, string> = {
  'Invalid login credentials': 'メールアドレスまたはパスワードが正しくありません',
  'Email not confirmed': 'メールアドレスの確認が完了していません',
};

export default function Login() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) navigate('/');
  }, [user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
      navigate('/');
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'エラーが発生しました';
      setError(ERROR_MAP[msg] ?? msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login">
      <div className="login__card">
        <h1 className="login__title">ログイン</h1>

        <form onSubmit={handleSubmit} className="login__form">
          <div className="login__field">
            <label className="login__label">メールアドレス</label>
            <input
              className="login__input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="login__field">
            <label className="login__label">パスワード</label>
            <div className="login__input-wrap">
              <input
                className="login__input"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
              <button type="button" className="login__eye" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? '非表示' : '表示'}
              </button>
            </div>
          </div>

          {error && <div className="error-banner">{error}</div>}

          <button type="submit" className="login__submit" disabled={loading}>
            {loading ? '処理中...' : 'ログイン'}
          </button>
        </form>

        <p className="login__switch">
          アカウントをお持ちでない方は<Link to="/signup">新規登録</Link>
        </p>
      </div>
    </main>
  );
}
