import React from 'react';
import { FullAnalysis, ComparisonAnalysis } from '../types/analysis';
import AnalysisCard from './AnalysisCard';

interface Props {
  analysis: FullAnalysis | null;
  comparison: ComparisonAnalysis | null;
}

const VERDICT_MAP = {
  clean:      { text: '可能性は低い', color: '#22c55e', bg: '#f0fdf4' },
  warning:    { text: '要注意',       color: '#f59e0b', bg: '#fffbeb' },
  suspicious: { text: '可能性が高い', color: '#ef4444', bg: '#fef2f2' },
};

function VerdictCard({ title, score, label }: { title: string; score: number; label: 'clean' | 'warning' | 'suspicious' }) {
  const cfg = VERDICT_MAP[label];
  return (
    <div className="verdict-card" style={{ background: cfg.bg, borderColor: cfg.color }}>
      <div>
        <h2 className="verdict-card__title">{title}</h2>
        <p className="verdict-card__sub" style={{ color: cfg.color }}>{cfg.text}</p>
      </div>
      <span className="verdict-card__score" style={{ color: cfg.color }}>
        {Math.round(score * 100)}
        <span className="verdict-card__unit"> / 100</span>
      </span>
    </div>
  );
}

export default function ResultsDashboard({ analysis, comparison }: Props) {
  if (!analysis && !comparison) return null;

  return (
    <div className="results">
      {analysis && (
        <>
          <div className="results__verdicts">
            <VerdictCard title="AI生成の可能性" score={analysis.ai_score} label={analysis.ai_label} />
            <VerdictCard title="人為的加工の可能性" score={analysis.manipulation_score} label={analysis.manipulation_label} />
          </div>

          <div className="results__cards">
            <p className="results__section-title">AI生成検出</p>
            <AnalysisCard title="Exifメタデータ解析" subtitle="AIツールのメタデータ署名を検出" result={analysis.exif} />
            <AnalysisCard title="周波数解析（FFT）" subtitle="GAN特有の周期パターンを検出" result={analysis.fft} />
            <AnalysisCard title="ピクセル統計解析" subtitle="ノイズレベル・彩度・色分布を分析" result={analysis.pixel_stats} />
            <AnalysisCard title="エッジ・カラーパレット解析" subtitle="エッジの鋭さと色数でアニメAI画像を検出" result={analysis.ai_features} />

            <p className="results__section-title">人為的加工検出</p>
            <AnalysisCard title="ELA解析" subtitle="JPEG再圧縮アーティファクトで編集箇所を検出" result={analysis.ela} />
            <AnalysisCard title="明るさ・コントラスト・彩度解析" subtitle="ヒストグラムのギャップ・クリッピング・彩度異常を検出" result={analysis.manipulation} />

            <p className="results__section-title">情報</p>
            <AnalysisCard title="顔検出" subtitle="顔の有無と位置を検出" result={analysis.face_detection} />
          </div>
        </>
      )}

      {comparison && (
        <div className="results__cards">
          <p className="results__section-title">比較結果</p>
          <AnalysisCard title="差分検出" subtitle="2枚の画像の違いをハイライト" result={comparison.diff} />
          <AnalysisCard title="類似度比較" subtitle="2枚の画像の類似度を数値化" result={comparison.similarity} />
        </div>
      )}
    </div>
  );
}
