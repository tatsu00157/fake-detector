import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabase';
import { createPortalSession } from '../api/client';

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isPremium, setIsPremium] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [loadingPortal, setLoadingPortal] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    supabase
      .from('subscriptions')
      .select('status')
      .eq('user_id', user.id)
      .single()
      .then(({ data }) => {
        setIsPremium(data?.status === 'active');
        setLoadingStatus(false);
      });
  }, [user, navigate]);

  const handlePortal = async () => {
    setLoadingPortal(true);
    try {
      const { url } = await createPortalSession();
      window.location.href = url;
    } catch {
      alert('エラーが発生しました。再度お試しください。');
    } finally {
      setLoadingPortal(false);
    }
  };

  if (!user) return null;

  return (
    <main className="dashboard">
      <div className="dashboard__inner">
        <h1 className="dashboard__title">ダッシュボード</h1>

        <section className="dashboard__card">
          <h2 className="dashboard__section-title">現在のプラン</h2>
          {loadingStatus ? (
            <p className="dashboard__loading">読み込み中...</p>
          ) : (
            <div className="dashboard__plan">
              <span className={`dashboard__plan-badge ${isPremium ? 'dashboard__plan-badge--premium' : ''}`} translate="no">
                {isPremium ? 'プレミアム' : '無料'}
              </span>
              {isPremium ? (
                <button
                  className="dashboard__btn dashboard__btn--portal"
                  onClick={handlePortal}
                  disabled={loadingPortal}
                >
                  {loadingPortal ? '処理中...' : 'プランを管理する・解約する'}
                </button>
              ) : (
                <button
                  className="dashboard__btn dashboard__btn--upgrade"
                  onClick={() => navigate('/pricing')}
                >
                  プレミアムにアップグレード
                </button>
              )}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
