import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) navigate('/login');
  }, [user, navigate]);

  if (!user) return null;

  return (
    <main className="dashboard">
      <div className="dashboard__inner">
        <h1 className="dashboard__title">ダッシュボード</h1>

        <section className="dashboard__card">
          <h2 className="dashboard__section-title">アカウント情報</h2>
          <p className="dashboard__email">{user.email}</p>
        </section>
      </div>
    </main>
  );
}
