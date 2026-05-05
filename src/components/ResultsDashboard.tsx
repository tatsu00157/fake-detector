import React from 'react';
import { FullAnalysis, ComparisonAnalysis } from '../types/analysis';
import AnalysisCard from './AnalysisCard';

interface Props {
  analysis: FullAnalysis | null;
  comparison: ComparisonAnalysis | null;
}

const SCORE_COLOR = (score: number) =>
  score < 0.3 ? '#22c55e' : score < 0.6 ? '#f59e0b' : '#ef4444';
const SCORE_BG = (score: number) =>
  score < 0.3 ? '#f0fdf4' : score < 0.6 ? '#fffbeb' : '#fef2f2';

function VerdictCard({ title, score }: { title: string; score: number }) {
  const color = SCORE_COLOR(score);
  const bg = SCORE_BG(score);
  return (
    <div className="verdict-card" style={{ background: bg, borderColor: color }}>
      <h2 className="verdict-card__title">{title}</h2>
      <span className="verdict-card__score" style={{ color }}>
        {Math.round(score * 100)}
        <span className="verdict-card__unit">%</span>
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
            <VerdictCard title="AI生成スコア" score={analysis.ai_score} />
            <VerdictCard title="加工スコア" score={analysis.manipulation_score} />
          </div>

          <div className="results__cards">
            <p className="results__section-title">AI生成検出</p>
            <AnalysisCard title="Exifメタデータ解析" subtitle="AIツールのメタデータ署名を検出" result={analysis.exif} />
            <AnalysisCard title="周波数解析（FFT）" subtitle="GAN特有の周期パターンを検出" result={analysis.fft} />
            <AnalysisCard title="ピクセル統計解析" subtitle="ノイズレベル・彩度・色分布を分析" result={analysis.pixel_stats} />
            <AnalysisCard title="エッジ・カラーパレット解析" subtitle="エッジの鋭さと色数でアニメAI画像を検出" result={analysis.ai_features} />

            <p className="results__section-title">人為的加工検出</p>
            <AnalysisCard title="ELA解析" subtitle="JPEG再圧縮アーティファクトで編集箇所を検出" result={analysis.ela} />
            <AnalysisCard title="ノイズ残差マップ" subtitle="ノイズパターンの不整合から合成・切り貼り箇所を可視化" result={analysis.prnu} />

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
