import React from 'react';
import { FullAnalysis, ComparisonAnalysis } from '../types/analysis';
import AnalysisCard from './AnalysisCard';

interface Props {
  analysis: FullAnalysis | null;
  comparison: ComparisonAnalysis | null;
}

const OVERALL_MAP = {
  clean:      { text: '改ざんの痕跡は検出されませんでした',   color: '#22c55e', bg: '#f0fdf4' },
  warning:    { text: '一部に要注意な点が見つかりました',     color: '#f59e0b', bg: '#fffbeb' },
  suspicious: { text: '改ざんまたはAI生成の可能性が高いです', color: '#ef4444', bg: '#fef2f2' },
};

export default function ResultsDashboard({ analysis, comparison }: Props) {
  if (!analysis && !comparison) return null;

  return (
    <div className="results">
      {analysis && (
        <>
          <div
            className="results__overall"
            style={{
              background: OVERALL_MAP[analysis.overall_label].bg,
              borderColor: OVERALL_MAP[analysis.overall_label].color,
            }}
          >
            <div>
              <h2 className="results__overall-title">総合判定</h2>
              <p className="results__overall-sub">{OVERALL_MAP[analysis.overall_label].text}</p>
            </div>
            <span className="results__overall-score" style={{ color: OVERALL_MAP[analysis.overall_label].color }}>
              {Math.round(analysis.overall_score * 100)}
              <span className="results__overall-unit"> / 100</span>
            </span>
          </div>

          <div className="results__cards">
            <p className="results__section-title">AI生成検出</p>
            <AnalysisCard title="Exifメタデータ解析" subtitle="AIツールのメタデータ署名を検出" result={analysis.exif} />
            <AnalysisCard title="周波数解析（FFT）" subtitle="GAN特有の周期パターンを検出" result={analysis.fft} />
            <AnalysisCard title="ピクセル統計解析" subtitle="AI画像特有の輝度・色分布を分析" result={analysis.pixel_stats} />

            <p className="results__section-title">人為的加工検出</p>
            <AnalysisCard title="ELA解析" subtitle="JPEG再圧縮アーティファクトで編集箇所を検出" result={analysis.ela} />
            <AnalysisCard title="クローンスタンプ検出" subtitle="コピー&amp;ペースト領域を検出" result={analysis.clone_detection} />

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
