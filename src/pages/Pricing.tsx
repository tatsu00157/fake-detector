import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { createCheckoutSession } from '../api/client';

type Feature = { label: string; free: boolean; premium: boolean };

const FEATURES: Feature[] = [
  { label: '1日の解析回数', free: false, premium: false },
  { label: 'Exifメタデータ解析・AI署名チェック', free: true, premium: true },
  { label: 'ELA解析（加工箇所の検出）', free: true, premium: true },
  { label: '周波数解析（GAN特有ノイズ検出）', free: true, premium: true },
  { label: 'テクスチャ解析（AI特有の滑らかさ検出）', free: true, premium: true },
  { label: 'ノイズレベル解析（AI生成の判定）', free: true, premium: true },
  { label: 'ノイズ残差マップ（合成箇所の可視化）', free: true, premium: true },
  { label: '顔検出', free: true, premium: true },
  { label: '2枚比較・差分検出', free: true, premium: true },
  { label: 'PDFレポート出力', free: false, premium: true },
  { label: '解析履歴の保存', free: false, premium: true },
];

export default function Pricing() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSubscribe = async () => {
    if (!user) {
      navigate('/signup');
      return;
    }
    setLoading(true);
    try {
      const { url } = await createCheckoutSession();
      window.location.href = url;
    } catch {
      alert('エラーが発生しました。再度お試しください。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="pricing">
      <div className="pricing__hero">
        <h1 className="pricing__title">料金プラン</h1>
        <p className="pricing__desc">まずは無料でお試しください</p>
      </div>

      <div className="pricing__cards">
        <div className="pricing__card">
          <div className="pricing__card-header">
            <h2 className="pricing__plan-name">無料</h2>
            <div className="pricing__price">
              <span className="pricing__amount">0</span>
              <span className="pricing__unit">円/月</span>
            </div>
            <p className="pricing__limit">ゲスト：3回/日・登録後：10回/日</p>
          </div>
          <button className="pricing__btn pricing__btn--free" onClick={() => navigate('/signup')}>
            無料で登録する
          </button>
        </div>

        <div className="pricing__card pricing__card--premium">
          <div className="pricing__badge">おすすめ</div>
          <div className="pricing__card-header">
            <h2 className="pricing__plan-name">プレミアム</h2>
            <div className="pricing__price">
              <span className="pricing__amount">980</span>
              <span className="pricing__unit">円/月</span>
            </div>
            <p className="pricing__limit">解析回数：無制限</p>
          </div>
          <button
            className="pricing__btn pricing__btn--premium"
            onClick={handleSubscribe}
            disabled={loading}
          >
            {loading ? '処理中...' : '始める'}
          </button>
        </div>
      </div>

      <div className="pricing__table-wrap">
        <table className="pricing__table">
          <thead>
            <tr>
              <th className="pricing__th pricing__th--feature">機能</th>
              <th className="pricing__th">無料</th>
              <th className="pricing__th pricing__th--premium">プレミアム</th>
            </tr>
          </thead>
          <tbody>
            {FEATURES.map((f) => (
              <tr key={f.label} className="pricing__tr">
                <td className="pricing__td pricing__td--feature">
                  {f.label === '1日の解析回数' ? (
                    <span>{f.label}</span>
                  ) : f.label}
                </td>
                <td className="pricing__td">
                  {f.label === '1日の解析回数' ? (
                    <span className="pricing__limit-text">3回（ゲスト）<br />10回（登録）</span>
                  ) : f.free ? (
                    <span className="pricing__check">✓</span>
                  ) : (
                    <span className="pricing__cross">—</span>
                  )}
                </td>
                <td className="pricing__td">
                  {f.label === '1日の解析回数' ? (
                    <span className="pricing__check">無制限</span>
                  ) : f.premium ? (
                    <span className="pricing__check">✓</span>
                  ) : (
                    <span className="pricing__cross">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
