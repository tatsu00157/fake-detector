import React, { useState } from 'react';
import UploadZone from '../components/UploadZone';
import ResultsDashboard from '../components/ResultsDashboard';
import { FullAnalysis } from '../types/analysis';

type Mode = 'single' | 'compare';

const DUMMY: FullAnalysis = {
  overall_score: 0.72,
  overall_label: 'suspicious',
  exif:           { score: 0.9,  label: 'suspicious', details: { ai_signatures: ['stable diffusion'], software: 'Stable Diffusion' }, image: null },
  ela:            { score: 0.45, label: 'warning',    details: { mean_error: 3.2, std_error: 12.1, is_jpeg: true }, image: null },
  fft:            { score: 0.61, label: 'suspicious', details: { peak_ratio: 0.012, peak_pixels: 320 }, image: null },
  pixel_stats:    { score: 0.4,  label: 'warning',    details: { suspicious_signals: 2 }, image: null },
  clone_detection:{ score: 0.1,  label: 'clean',      details: { clone_pairs_found: 4 }, image: null },
  face_detection: { score: 0.0,  label: 'info',       details: { face_count: 1, faces: [{ x: 120, y: 80, w: 90, h: 90 }] }, image: null },
};

export default function Home() {
  const [mode, setMode] = useState<Mode>('single');
  const [previews, setPreviews] = useState<string[]>([]);
  const [showDummy, setShowDummy] = useState(false);

  const handleFiles = (newFiles: File[]) => {
    setShowDummy(true);
    if (mode === 'compare') {
      setPreviews((prev) => {
        const urls = newFiles.map((f) => URL.createObjectURL(f));
        return [...prev, ...urls].slice(0, 2);
      });
    } else {
      setPreviews(newFiles.map((f) => URL.createObjectURL(f)));
    }
  };

  const handleModeChange = (next: Mode) => {
    setMode(next);
    setPreviews([]);
    setShowDummy(false);
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
        <UploadZone onFileSelect={handleFiles} mode={mode} />

        {previews.length > 0 && (
          <div className="preview">
            {previews.map((url, i) => (
              <img key={i} src={url} alt={`preview ${i + 1}`} className="preview__img" />
            ))}
          </div>
        )}
      </div>

      <ResultsDashboard analysis={showDummy ? DUMMY : null} comparison={null} />
    </main>
  );
}
