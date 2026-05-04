import React, { useState } from 'react';
import UploadZone from '../components/UploadZone';

type Mode = 'single' | 'compare';

export default function Home() {
  const [mode, setMode] = useState<Mode>('single');
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);

  const handleFiles = (newFiles: File[]) => {
    if (mode === 'compare') {
      setFiles((prev) => {
        const updated = [...prev, ...newFiles].slice(0, 2);
        setPreviews(updated.map((f) => URL.createObjectURL(f)));
        return updated;
      });
    } else {
      setFiles(newFiles);
      setPreviews(newFiles.map((f) => URL.createObjectURL(f)));
    }
  };

  const handleModeChange = (next: Mode) => {
    setMode(next);
    setFiles([]);
    setPreviews([]);
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
    </main>
  );
}
