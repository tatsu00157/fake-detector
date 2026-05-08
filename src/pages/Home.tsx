import React, { useState } from 'react';
import UploadZone from '../components/UploadZone';
import ResultsDashboard from '../components/ResultsDashboard';
import { analyzeImage, compareImages } from '../api/client';
import { FullAnalysis, ComparisonAnalysis } from '../types/analysis';

type Mode = 'single' | 'compare';

export default function Home() {
  const [mode, setMode] = useState<Mode>('single');
  const [previews, setPreviews] = useState<(string | null)[]>([null, null]);
  const [files, setFiles] = useState<(File | null)[]>([null, null]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<FullAnalysis | null>(null);
  const [comparison, setComparison] = useState<ComparisonAnalysis | null>(null);

  const handleSingleFile = async (newFiles: File[]) => {
    setError(null);
    const file = newFiles[0];
    setFiles([file, null]);
    setPreviews([URL.createObjectURL(file), null]);
    setAnalysis(null);
    setLoading(true);
    try {
      setAnalysis(await analyzeImage(file));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '解析中にエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handleCompareFile = async (index: number, newFiles: File[]) => {
    setError(null);
    const updatedFiles: (File | null)[] = [...files];
    const updatedPreviews: (string | null)[] = [...previews];
    updatedFiles[index] = newFiles[0];
    updatedPreviews[index] = URL.createObjectURL(newFiles[0]);
    setFiles(updatedFiles);
    setPreviews(updatedPreviews);
    setComparison(null);

    if (updatedFiles[0] && updatedFiles[1]) {
      setLoading(true);
      try {
        setComparison(await compareImages(updatedFiles[0], updatedFiles[1]));
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : '解析中にエラーが発生しました');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleRemoveSlot = (index: number) => {
    const updatedFiles: (File | null)[] = [...files];
    const updatedPreviews: (string | null)[] = [...previews];
    updatedFiles[index] = null;
    updatedPreviews[index] = null;
    setFiles(updatedFiles);
    setPreviews(updatedPreviews);
    setComparison(null);
    if (index === 0) setAnalysis(null);
  };

  const handleReset = () => {
    setFiles([null, null]);
    setPreviews([null, null]);
    setAnalysis(null);
    setComparison(null);
    setError(null);
  };

  const handleModeChange = (next: Mode) => {
    setMode(next);
    handleReset();
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
        {mode === 'single' && (
          <div className={`upload-layout${files[0] ? ' upload-layout--split' : ' upload-layout--center'}`}>
            <div className="upload-slot">
              <UploadZone onFileSelect={handleSingleFile} mode="single" disabled={loading} />
            </div>
            {files[0] && previews[0] && (
              <div className="upload-slot">
                <div className="preview-box">
                  <img src={previews[0]} alt="preview" className="preview-box__img" />
                  <button className="preview-box__delete" onClick={handleReset}>削除</button>
                </div>
              </div>
            )}
          </div>
        )}

        {mode === 'compare' && (
          <>
            <div className="upload-layout upload-layout--split">
              {([0, 1] as const).map((i) => (
                <div key={i} className="upload-slot">
                  {previews[i] ? (
                    <div className="preview-box">
                      <img src={previews[i]!} alt={`preview ${i + 1}`} className="preview-box__img" />
                      <button className="preview-box__delete" onClick={() => handleRemoveSlot(i)}>削除</button>
                    </div>
                  ) : (
                    <UploadZone
                      onFileSelect={(f) => handleCompareFile(i, f)}
                      mode="single"
                      disabled={loading}
                    />
                  )}
                </div>
              ))}
            </div>
            {files[0] && !files[1] && !loading && (
              <p className="upload-zone__sub" style={{ textAlign: 'center', marginTop: '0.75rem' }}>
                2枚目の画像をアップロードしてください
              </p>
            )}
          </>
        )}
      </div>

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
