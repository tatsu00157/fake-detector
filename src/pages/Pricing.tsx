import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { createCheckoutSession } from '../api/client';

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
    } catch (e) {
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
          </div>
          <ul className="pricing__features">
            <li>ゲスト：1日3回まで</li>
            <li>登録後：1日10回まで</li>
            <li>基本解析（メタデータ・ELA・テクスチャなど）</li>
            <li>画像比較</li>
          </ul>
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
          </div>
          <ul className="pricing__features">
            <li>解析回数：無制限</li>
            <li>全解析機能</li>
            <li>履歴保存（30日間）</li>
            <li>PDFレポート出力</li>
          </ul>
          <button
            className="pricing__btn pricing__btn--premium"
            onClick={handleSubscribe}
            disabled={loading}
          >
            {loading ? '処理中...' : '始める'}
          </button>
        </div>
      </div>
    </main>
  );
}
