import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { useAuth } from '../context/AuthContext';

const ERROR_MAP: Record<string, string> = {
  'User already registered': 'このメールアドレスは既に登録されています',
};

function validatePassword(pw: string) {
  return {
    length: pw.length >= 8,
    letter: /[a-zA-Z]/.test(pw),
    number: /[0-9]/.test(pw),
    symbol: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pw),
  };
}

export default function Signup() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) navigate('/');
  }, [user, navigate]);

  const checks = validatePassword(password);
  const isPasswordValid = Object.values(checks).every(Boolean);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!isPasswordValid) {
      setError('パスワードの要件を満たしていません');
      return;
    }
    if (password !== confirmPassword) {
      setError('パスワードが一致しません');
      return;
    }
    setLoading(true);
    try {
      const { error } = await supabase.auth.signUp({ email, password });
      if (error) throw error;
      setMessage('確認メールを送信しました。メールを確認してからログインしてください。');
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
        <h1 className="login__title">新規登録</h1>

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
                autoComplete="new-password"
              />
              <button type="button" className="login__eye" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? '非表示' : '表示'}
              </button>
            </div>
            <ul className="login__requirements">
              <li className={checks.length ? 'met' : ''}>8文字以上</li>
              <li className={checks.letter ? 'met' : ''}>英字を含む</li>
              <li className={checks.number ? 'met' : ''}>数字を含む</li>
              <li className={checks.symbol ? 'met' : ''}>記号を含む（例：!@#$%）</li>
            </ul>
          </div>

          <div className="login__field">
            <label className="login__label">パスワード（確認）</label>
            <div className="login__input-wrap">
              <input
                className="login__input"
                type={showConfirm ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                autoComplete="new-password"
              />
              <button type="button" className="login__eye" onClick={() => setShowConfirm(!showConfirm)}>
                {showConfirm ? '非表示' : '表示'}
              </button>
            </div>
          </div>

          {error && <div className="error-banner">{error}</div>}
          {message && <div className="success-banner">{message}</div>}

          <button type="submit" className="login__submit login__submit--pink" disabled={loading}>
            {loading ? '処理中...' : '登録する'}
          </button>
        </form>

        <p className="login__switch">
          すでにアカウントをお持ちの方は<Link to="/login">ログイン</Link>
        </p>
      </div>
    </main>
  );
}
