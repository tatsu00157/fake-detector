import React from 'react';
import { FullAnalysis, ComparisonAnalysis } from '../types/analysis';
import AnalysisCard from './AnalysisCard';

interface Props {
  analysis: FullAnalysis | null;
  comparison: ComparisonAnalysis | null;
}

export default function ResultsDashboard({ analysis, comparison }: Props) {
  if (!analysis && !comparison) return null;

  return (
    <div className="results">
      {analysis && (
        <div className="results__cards">
          <p className="results__section-title">AI生成検出</p>
          <AnalysisCard title="メタデータ解析" subtitle="AI生成ツールの署名・撮影情報・改ざん痕跡を検出" result={analysis.exif} />
          <AnalysisCard title="テクスチャ分析" subtitle="不自然に滑らかな領域を赤でハイライト（AI画像に特有）" result={analysis.texture} />
          <AnalysisCard title="ノイズレベル解析" subtitle="ノイズが少なすぎる領域を赤でハイライト（AI画像に特有）" result={analysis.noise} />

          <p className="results__section-title">加工検出</p>
          <AnalysisCard title="ELA解析" subtitle="編集・加工された箇所を画像で可視化" result={analysis.ela} />
          <AnalysisCard title="ノイズ残差マップ" subtitle="別画像から合成・切り貼りされた箇所を赤でハイライト" result={analysis.prnu} />
        </div>
      )}

      {comparison && (
        <div className="results__cards">
          <AnalysisCard title="差分検出" subtitle="2枚の画像の違いをハイライト" result={comparison.diff} />
          <AnalysisCard title="類似度比較" subtitle="2枚の画像の類似度を数値化" result={comparison.similarity} />
        </div>
      )}
    </div>
  );
}
