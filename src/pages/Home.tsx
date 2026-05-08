import React, { useState } from 'react';
import UploadZone from '../components/UploadZone';
import ResultsDashboard from '../components/ResultsDashboard';
import ExplanationsSection from '../components/ExplanationsSection';
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

  const handleSingleFile = (newFiles: File[]) => {
    setError(null);
    setAnalysis(null);
    const file = newFiles[0];
    setFiles([file, null]);
    setPreviews([URL.createObjectURL(file), null]);
  };

  const handleCompareFile = (index: number, newFiles: File[]) => {
    setError(null);
    setComparison(null);
    const updatedFiles: (File | null)[] = [...files];
    const updatedPreviews: (string | null)[] = [...previews];
    updatedFiles[index] = newFiles[0];
    updatedPreviews[index] = URL.createObjectURL(newFiles[0]);
    setFiles(updatedFiles);
    setPreviews(updatedPreviews);
  };

  const handleAnalyze = async () => {
    if (!files[0]) return;
    setError(null);
    setAnalysis(null);
    setLoading(true);
    try {
      setAnalysis(await analyzeImage(files[0]));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '解析中にエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async () => {
    if (!files[0] || !files[1]) return;
    setError(null);
    setComparison(null);
    setLoading(true);
    try {
      setComparison(await compareImages(files[0], files[1]));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '解析中にエラーが発生しました');
    } finally {
      setLoading(false);
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

  const canAnalyze = mode === 'single' ? !!files[0] : !!(files[0] && files[1]);

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
                <div className={`preview-box${loading ? ' preview-box--scanning' : ''}`}>
                  <img src={previews[0]} alt="preview" className="preview-box__img" />
                  {loading && <div className="scan-line" />}
                  {!loading && (
                    <button className="preview-box__delete" onClick={handleReset}>削除</button>
                  )}
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
                    <div className={`preview-box${loading ? ' preview-box--scanning' : ''}`}>
                      <img src={previews[i]!} alt={`preview ${i + 1}`} className="preview-box__img" />
                      {loading && <div className="scan-line" />}
                      {!loading && (
                        <button className="preview-box__delete" onClick={() => handleRemoveSlot(i)}>削除</button>
                      )}
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

        {canAnalyze && !loading && (
          <div className="analyze-action">
            <button
              className="analyze-btn"
              onClick={mode === 'single' ? handleAnalyze : handleCompare}
            >
              {mode === 'single' ? '解析する' : '比較する'}
            </button>
          </div>
        )}

        {loading && (
          <div className="scanning-status">
            <span className="scanning-status__dot" />
            <span className="scanning-status__dot" />
            <span className="scanning-status__dot" />
            <p>スキャン中...</p>
          </div>
        )}
      </div>

      {error && <div className="error-banner"><strong>エラー: </strong>{error}</div>}

      <ResultsDashboard analysis={analysis} comparison={comparison} />
      <ExplanationsSection />
    </main>
  );
}
