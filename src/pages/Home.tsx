import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import UploadZone from '../components/UploadZone';
import ResultsDashboard from '../components/ResultsDashboard';
import { analyzeImage, compareImages } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { FullAnalysis, ComparisonAnalysis } from '../types/analysis';

type Mode = 'single' | 'compare';

const GUEST_LIMIT = 3;

function getGuestCount(): number {
  const today = new Date().toDateString();
  const stored = localStorage.getItem('guest_usage');
  if (!stored) return 0;
  const { date, count } = JSON.parse(stored);
  return date === today ? count : 0;
}

function incrementGuestCount(): void {
  const today = new Date().toDateString();
  const current = getGuestCount();
  localStorage.setItem('guest_usage', JSON.stringify({ date: today, count: current + 1 }));
}

export default function Home() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<Mode>('single');
  const [previews, setPreviews] = useState<string[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [guestLimitReached, setGuestLimitReached] = useState(false);
  const [analysis, setAnalysis] = useState<FullAnalysis | null>(null);
  const [comparison, setComparison] = useState<ComparisonAnalysis | null>(null);

  const handleFiles = async (newFiles: File[]) => {
    if (!user) {
      if (getGuestCount() >= GUEST_LIMIT) {
        setGuestLimitReached(true);
        return;
      }
      incrementGuestCount();
    }

    setError(null);
    setGuestLimitReached(false);

    if (mode === 'compare') {
      const updated = [...files, ...newFiles].slice(0, 2);
      setFiles(updated);
      setPreviews(updated.map((f) => URL.createObjectURL(f)));

      if (updated.length === 2) {
        setLoading(true);
        setComparison(null);
        try {
          setComparison(await compareImages(updated[0], updated[1]));
        } catch (e: unknown) {
          setError(e instanceof Error ? e.message : '解析中にエラーが発生しました');
        } finally {
          setLoading(false);
        }
      }
    } else {
      setFiles([newFiles[0]]);
      setPreviews([URL.createObjectURL(newFiles[0])]);
      setAnalysis(null);
      setLoading(true);
      try {
        setAnalysis(await analyzeImage(newFiles[0]));
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : '解析中にエラーが発生しました');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleModeChange = (next: Mode) => {
    setMode(next);
    setPreviews([]);
    setFiles([]);
    setAnalysis(null);
    setComparison(null);
    setError(null);
    setGuestLimitReached(false);
  };

  const handleReset = () => {
    setPreviews([]);
    setFiles([]);
    setAnalysis(null);
    setComparison(null);
    setError(null);
    setGuestLimitReached(false);
  };

  return (
    <main className="home">
      <div className="home__hero">
        <h1 className="home__title">フェイク画像を検出する</h1>
        <p className="home__desc">AI生成画像・人為的加工を多角的に解析します</p>

        <div className="mode-toggle">
          <button
            className={`mode-toggle__btn${mode === 'single' ? ' mode-toggle__btn--active' : ''}`}
            onClick={() => handleModeChange('single')}
          >
            1枚解析
          </button>
          <button
            className={`mode-toggle__btn${mode === 'compare' ? ' mode-toggle__btn--active' : ''}`}
            onClick={() => handleModeChange('compare')}
          >
            2枚比較
          </button>
        </div>
      </div>

      <div className="home__upload">
        {previews.length > 0 && (
          <div className="upload-actions">
            <button className="delete-btn" onClick={handleReset}>削除</button>
          </div>
        )}

        <UploadZone onFileSelect={handleFiles} mode={mode} disabled={loading} />

        {previews.length > 0 && (
          <div className="preview">
            {previews.map((url, i) => (
              <img key={i} src={url} alt={`preview ${i + 1}`} className="preview__img" />
            ))}
          </div>
        )}

        {mode === 'compare' && files.length === 1 && !loading && (
          <p className="upload-zone__sub" style={{ textAlign: 'center', marginTop: '0.5rem' }}>
            2枚目の画像をアップロードしてください
          </p>
        )}
      </div>

      {guestLimitReached && (
        <div className="guest-limit">
          <p className="guest-limit__text">ゲストの無料利用回数（{GUEST_LIMIT}回/日）に達しました</p>
          <p className="guest-limit__sub">無料登録すると1日10回まで利用できます</p>
          <div className="guest-limit__actions">
            <button className="guest-limit__signup" onClick={() => navigate('/login?mode=signup')}>無料で登録する</button>
            <button className="guest-limit__login" onClick={() => navigate('/login')}>ログイン</button>
          </div>
        </div>
      )}

      {loading && (
        <div className="loading">
          <div className="loading__spinner" />
          <p>解析中...</p>
        </div>
      )}

      {error && <div className="error-banner"><strong>エラー: </strong>{error}</div>}

      <ResultsDashboard analysis={analysis} comparison={comparison} />
    </main>
  );
}
