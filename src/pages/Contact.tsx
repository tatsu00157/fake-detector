import React from 'react';

const CONTACT_EMAIL = 'support@karineffort.com';

const categories = [
  {
    title: '機能の要望・提案',
    body: '「こんな機能があると便利」「この検出指標を追加してほしい」など、サービス改善のご提案をお待ちしています。',
  },
  {
    title: 'バグ・不具合の報告',
    body: '解析が動かない、エラーが出る、表示がおかしいなど、お気軽にお知らせください。',
  },
  {
    title: '解析結果についての質問',
    body: 'スコアの見方、各指標の意味、結果の解釈についてご不明な点はお問い合わせください。',
  },
  {
    title: 'メディア掲載・連携のご相談',
    body: '取材・掲載・コラボレーションなどのご相談も歓迎しています。',
  },
];

export default function Contact() {
  return (
    <main className="legal-page">
      <div className="legal-inner">
        <h1>お問い合わせ</h1>
        <p className="legal-updated">ご意見・ご要望をお待ちしております</p>

        <section>
          <h2>このようなお問い合わせをお待ちしています</h2>
          <div className="contact-categories">
            {categories.map((cat) => (
              <div key={cat.title} className="contact-category">
                <h3>{cat.title}</h3>
                <p>{cat.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2>お問い合わせ方法</h2>
          <p>下記のボタンからメールにてお気軽にご連絡ください。</p>
          <p>通常2〜3営業日以内にご返信いたします。</p>
          <a href={`mailto:${CONTACT_EMAIL}`} className="contact-btn">
            メールで問い合わせる
          </a>
        </section>

        <section>
          <h2>運営者情報</h2>
          <p>運営：【屋号】</p>
          <p>メールアドレス：{CONTACT_EMAIL}</p>
        </section>
      </div>
    </main>
  );
}
