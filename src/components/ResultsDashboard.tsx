import React, { useState } from 'react';
import { FullAnalysis, ComparisonAnalysis, AnalysisResult } from '../types/analysis';

interface Props {
  analysis: FullAnalysis | null;
  comparison: ComparisonAnalysis | null;
}

interface TabDef {
  key: string;
  label: string;
  result: AnalysisResult;
}

const LABEL_MAP: Record<string, { text: string; color: string }> = {
  clean:      { text: '安全',     color: '#22c55e' },
  warning:    { text: '要注意',   color: '#f59e0b' },
  suspicious: { text: '疑わしい', color: '#ef4444' },
  info:       { text: '情報',     color: '#3b82f6' },
  error:      { text: 'エラー',   color: '#94a3b8' },
};

function renderValue(val: unknown): string {
  if (typeof val === 'object' && val !== null) return JSON.stringify(val, null, 2);
  return String(val);
}

function TabSection({ title, score, label, tabs }: {
  title: string;
  score: number;
  label: string;
  tabs: TabDef[];
}) {
  const [active, setActive] = useState(0);
  const sectionCfg = LABEL_MAP[label] ?? LABEL_MAP.error;
  const current = tabs[active];
  const tabCfg = LABEL_MAP[current.result.label] ?? LABEL_MAP.error;
  const pct = Math.round(current.result.score * 100);

  return (
    <div className="result-section">
      <div className="result-section__header">
        <h2 className="result-section__title">{title}</h2>
        <div className="result-section__summary">
          <span className="result-section__badge" style={{ background: sectionCfg.color }}>
            {sectionCfg.text}
          </span>
          <span className="result-section__score-num">{(score * 100).toFixed(1)}%</span>
        </div>
      </div>

      <div className="result-tabs">
        {tabs.map((tab, i) => {
          const tc = LABEL_MAP[tab.result.label] ?? LABEL_MAP.error;
          return (
            <button
              key={tab.key}
              className={`result-tab${active === i ? ' result-tab--active' : ''}`}
              onClick={() => setActive(i)}
            >
              <span className="result-tab__dot" style={{ background: tc.color }} />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="result-content">
        <div className="result-content__meta">
          <span className="result-content__label" style={{ background: tabCfg.color }}>
            {tabCfg.text}
          </span>
          {current.result.label !== 'info' && current.result.label !== 'error' && (
            <>
              <div className="result-content__bar">
                <div
                  className="result-content__bar-fill"
                  style={{ width: `${pct}%`, background: tabCfg.color }}
                />
              </div>
              <span className="result-content__pct">{pct}%</span>
            </>
          )}
        </div>

        {current.result.image && (
          <img
            src={current.result.image}
            alt={`${current.label} visualization`}
            className="result-content__img"
          />
        )}

        <dl className="result-content__details">
          {Object.entries(current.result.details)
            .filter(([k]) => k !== 'raw_tags')
            .map(([key, val]) => (
              <div key={key} className="result-content__detail-row">
                <dt>{key}</dt>
                <dd>{renderValue(val)}</dd>
              </div>
            ))}
        </dl>
      </div>
    </div>
  );
}

export default function ResultsDashboard({ analysis, comparison }: Props) {
  if (!analysis && !comparison) return null;

  return (
    <div className="results">
      <div className="results__disclaimer">
        ⚠️ 解析結果はあくまで参考情報です。各指標は可能性を示すものであり、画像の真正性を断定するものではありません。複数の指標を組み合わせて総合的に判断してください。
      </div>
      {analysis && (
        <>
          <TabSection
            title="AI生成検出"
            score={analysis.ai_score}
            label={analysis.ai_label}
            tabs={[
              { key: 'exif',    label: 'メタデータ',   result: analysis.exif },
              { key: 'texture', label: 'テクスチャ',   result: analysis.texture },
              { key: 'noise',   label: 'ノイズレベル', result: analysis.noise },
            ]}
          />
          <TabSection
            title="加工検出"
            score={analysis.manipulation_score}
            label={analysis.manipulation_label}
            tabs={[
              { key: 'noise_consistency', label: 'ノイズ整合性',  result: analysis.noise_consistency },
              { key: 'dct',               label: 'DCT',           result: analysis.dct_splicing },
              ...(analysis.prnu ? [{ key: 'prnu', label: 'ノイズ残差マップ', result: analysis.prnu }] : []),
              { key: 'manipulation',      label: 'ノイズCoV',     result: analysis.manipulation },
              { key: 'ela',               label: 'ELA（参考）',   result: analysis.ela },
            ]}
          />
        </>
      )}

      {comparison && (
        <TabSection
          title="比較結果"
          score={comparison.similarity.score}
          label={comparison.similarity.label}
          tabs={[
            { key: 'diff',       label: '差分検出',   result: comparison.diff },
            { key: 'similarity', label: '類似度比較', result: comparison.similarity },
          ]}
        />
      )}
    </div>
  );
}
