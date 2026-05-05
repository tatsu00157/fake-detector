import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { useAuth } from '../context/AuthContext';

type Mode = 'login' | 'signup';

const ERROR_MAP: Record<string, string> = {
  'Invalid login credentials': 'メールアドレスまたはパスワードが正しくありません',
  'Email not confirmed': 'メールアドレスの確認が完了していません',
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

export default function Login() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [mode, setMode] = useState<Mode>(searchParams.get('mode') === 'signup' ? 'signup' : 'login');
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
    setMessage(null);

    if (mode === 'signup') {
      if (!isPasswordValid) {
        setError('パスワードの要件を満たしていません');
        return;
      }
      if (password !== confirmPassword) {
        setError('パスワードが一致しません');
        return;
      }
    }

    setLoading(true);
    try {
      if (mode === 'login') {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        navigate('/');
      } else {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        setMessage('確認メールを送信しました。メールを確認してからログインしてください。');
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'エラーが発生しました';
      setError(ERROR_MAP[msg] ?? msg);
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (next: Mode) => {
    setMode(next);
    setError(null);
    setMessage(null);
    setPassword('');
    setConfirmPassword('');
  };

  return (
    <main className="login">
      <div className="login__card">
        <h1 className="login__title">FakeDetector</h1>
        <p className="login__subtitle">AI生成・加工画像の検出サービス</p>

        <div className="mode-toggle" style={{ marginBottom: '1.5rem' }}>
          <button
            className={`mode-toggle__btn${mode === 'login' ? ' mode-toggle__btn--active' : ''}`}
            onClick={() => switchMode('login')}
          >
            ログイン
          </button>
          <button
            className={`mode-toggle__btn${mode === 'signup' ? ' mode-toggle__btn--active' : ''}`}
            onClick={() => switchMode('signup')}
          >
            新規登録
          </button>
        </div>

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
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              />
              <button type="button" className="login__eye" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? '非表示' : '表示'}
              </button>
            </div>
            {mode === 'signup' && (
              <ul className="login__requirements">
                <li className={checks.length ? 'met' : ''}>8文字以上</li>
                <li className={checks.letter ? 'met' : ''}>英字を含む</li>
                <li className={checks.number ? 'met' : ''}>数字を含む</li>
                <li className={checks.symbol ? 'met' : ''}>記号を含む（例：!@#$%）</li>
              </ul>
            )}
          </div>

          {mode === 'signup' && (
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
          )}

          {error && <div className="error-banner">{error}</div>}
          {message && <div className="success-banner">{message}</div>}

          <button type="submit" className="login__submit" disabled={loading}>
            {loading ? '処理中...' : mode === 'login' ? 'ログイン' : '登録する'}
          </button>
        </form>
      </div>
    </main>
  );
}
