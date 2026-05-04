import React, { useState } from 'react';
import { AnalysisResult } from '../types/analysis';

interface Props {
  title: string;
  subtitle: string;
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

export default function AnalysisCard({ title, subtitle, result }: Props) {
  const [expanded, setExpanded] = useState(false);
  const cfg = LABEL_MAP[result.label] ?? LABEL_MAP.error;
  const pct = Math.round(result.score * 100);

  return (
    <div className="analysis-card">
      <div className="analysis-card__header" onClick={() => setExpanded(!expanded)}>
        <div className="analysis-card__title-group">
          <h3 className="analysis-card__title">{title}</h3>
          <span className="analysis-card__subtitle">{subtitle}</span>
        </div>
        <div className="analysis-card__right">
          <span className="analysis-card__label" style={{ background: cfg.color }}>
            {cfg.text}
          </span>
          {result.label !== 'info' && result.label !== 'error' && (
            <div className="analysis-card__bar">
              <div
                className="analysis-card__bar-fill"
                style={{ width: `${pct}%`, background: cfg.color }}
              />
            </div>
          )}
          <span className="analysis-card__toggle">{expanded ? '▲' : '▼'}</span>
        </div>
      </div>

      {expanded && (
        <div className="analysis-card__body">
          {result.image && (
            <img src={result.image} alt={`${title} visualization`} className="analysis-card__image" />
          )}
          <dl className="analysis-card__details">
            {Object.entries(result.details)
              .filter(([k]) => k !== 'raw_tags')
              .map(([key, val]) => (
                <div key={key} className="analysis-card__detail-row">
                  <dt className="analysis-card__dt">{key}</dt>
                  <dd className="analysis-card__dd">{renderValue(val)}</dd>
                </div>
              ))}
          </dl>
        </div>
      )}
    </div>
  );
}
