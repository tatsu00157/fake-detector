import React, { useState } from 'react';
import UploadZone from '../components/UploadZone';
import ResultsDashboard from '../components/ResultsDashboard';
import { analyzeImage } from '../api/client';
import { FullAnalysis } from '../types/analysis';

type Mode = 'single' | 'compare';

export default function Home() {
  const [mode, setMode] = useState<Mode>('single');
  const [previews, setPreviews] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<FullAnalysis | null>(null);

  const handleFiles = async (newFiles: File[]) => {
    if (mode === 'compare') {
      setPreviews((prev) => [...prev, ...newFiles.map((f) => URL.createObjectURL(f))].slice(0, 2));
    } else {
      setPreviews(newFiles.map((f) => URL.createObjectURL(f)));
    }

    setError(null);
    setAnalysis(null);
    setLoading(true);

    try {
      setAnalysis(await analyzeImage(newFiles[0]));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '解析中にエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handleModeChange = (next: Mode) => {
    setMode(next);
    setPreviews([]);
    setAnalysis(null);
    setError(null);
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
        <UploadZone onFileSelect={handleFiles} mode={mode} disabled={loading} />

        {previews.length > 0 && (
          <div className="preview">
            {previews.map((url, i) => (
              <img key={i} src={url} alt={`preview ${i + 1}`} className="preview__img" />
            ))}
          </div>
        )}
      </div>

      {loading && (
        <div className="loading">
          <div className="loading__spinner" />
          <p>解析中...</p>
        </div>
      )}

      {error && <div className="error-banner"><strong>エラー: </strong>{error}</div>}

      <ResultsDashboard analysis={analysis} comparison={null} />
    </main>
  );
}
