# フェイク画像・動画検出サービス 設計書

## ルール

- **コードの修正は「内容を説明→ユーザーの承認を待つ→修正実行」の順で行う。説明後は必ずユーザーの返答を待つ**
- **コードを修正したら必ずこのCLAUDE.mdを最新の状態に更新する**
- **CLAUDE.mdを更新したら必ずgit commit & pushをセットで行う**
- **APIキー・パスワード・個人情報などの機密情報は絶対にチャットに出力しない**

## 実装済み

### フロントエンド
- `src/App.tsx` — React Router導入。/・/privacy・/terms・/contactルート。認証関連ルートはUI非公開（コードは保持）
- `src/App.css` — グローバルスタイル（ヘッダー・ホーム・アップロードゾーンなど）
- `src/components/ScrollToTop.tsx` — ルート変更時に自動でページ最上部にスムーズスクロール
- `src/components/Header.tsx` — ロゴ（FakeScan・lang="en"）はホームへのリンク。ロゴ左にピンク（#f472b6）の虫眼鏡SVGアイコン。右側にホームリンク。ロゴ・ホームリンクはクリック時にスムーズスクロールで最上部へ
- `src/components/Footer.tsx` — フッター。ロゴとコピーライトにlang="en"設定。プライバシーポリシー・利用規約・お問い合わせリンク。ロゴ左にヘッダーと同じピンクの虫眼鏡SVGアイコン
- `src/components/UploadZone.tsx` — ドラッグ＆ドロップ対応アップロードUI（日本語テキスト）
- `src/components/AnalysisCard.tsx` — 解析項目カード（スコアバー・詳細展開・画像表示）
- `src/components/ResultsDashboard.tsx` — AI生成検出・加工検出をタブUI（メタデータ・テクスチャ・ノイズ等）で切り替え表示。セクションごとの総合スコアバッジ。タブに判定カラードット表示。結果上部に参考情報である旨の免責注意書き表示。スコア表示は小数点第一位。比較結果セクションはタブ切り替えでヘッダーのラベル・スコアが連動（useTabScore）。LABEL_MAPにdiff（差異率）・similarity（類似度）を追加（青・#3b82f6）。差分・類似度タブはスコアバー非表示・詳細欄に数値表示
- `src/components/ExplanationsSection.tsx` — 解析指標の説明・マップの見方・スコア基準。Home.tsxで常時表示。2枚比較（差分検出・類似度判定）の説明も含む。スコアの見方をAI生成検出・加工検出用と2枚比較用に分離して表示
- `src/types/analysis.ts` — 解析結果の型定義。noise_consistency・dct_splicing・prnu?。labelに'diff'|'similarity'を追加
- `src/lib/supabase.ts` — Supabaseクライアント
- `src/context/AuthContext.tsx` — 認証状態管理（ログイン・ログアウト・セッション）
- `src/api/client.ts` — 認証なし・シンプルなfetch。analyzeImage・compareImagesのみ。429エラーは日本語メッセージで表示
- `src/pages/Home.tsx` — ホームページ。利用制限なし・無制限。アップロード後は左にアップロードゾーン・右にプレビューを横並び表示。「解析する」「比較する」ボタンを押して解析開始。解析中はプレビュー上に走査線アニメーションとドットインジケーター表示。スマホは縦並びにフォールバック
- `src/pages/PrivacyPolicy.tsx` — プライバシーポリシーページ（/privacy）。10条のお問い合わせリンクは /contact へ。5条にGoogleアナリティクス（GA4）のCookie使用・オプトアウト方法を明記。7条にCookie説明（独自トラッキングなし・GA4は5条参照）
- `src/pages/Terms.tsx` — 利用規約ページ（/terms）。10条のお問い合わせリンクは /contact へ
- `src/pages/Contact.tsx` — お問い合わせページ（/contact）。お問い合わせ種類カード4種・メールリンク（件名【FakeScan】自動付与・本文テンプレートに件名変更しないよう注記）・「内容によってはご返信できない場合がある」免責文・運営者情報（屋号：Karin Lab）。連絡先はcontact@karineffort.com
- `src/pages/Login.tsx` — ログインページ。下部に新規登録へのリンク
- `src/pages/Signup.tsx` — 新規登録ページ。パスワード表示切替・要件リアルタイム表示（8文字以上・英字・数字・記号）・パスワード確認欄
- `src/pages/Dashboard.tsx` — ダッシュボードページ。ログイン中のメールアドレスを表示
- `public/index.html` — lang="ja"設定・タイトル・meta description・OGP・Twitter Card設定済み。og:url=https://fakescan.karineffort.com。noscriptは日本語。GoogleアナリティクスGA4（gtag.js）埋め込み済み
- `public/manifest.json` — short_name=FakeScan・theme_color=#0f172a・background_color=#f8fafc設定済み
- `public/favicon.svg` — ネイビー背景＋ピンク虫眼鏡のSVGファビコン
- `public/sitemap.xml` — /・/privacy・/terms・/contactの4ページ記載
- `public/robots.txt` — Sitemapディレクティブにsitemap.xmlのURLを指定
- ブランドカラー：ピンク（`#f472b6`）を登録系CTAボタンに使用

### バックエンド
- `backend/main.py` — FastAPIアプリ本体。slowapiのlimiterをapp.state登録・429ハンドラー追加。SecurityHeadersMiddleware（X-Content-Type-Options等）。本番環境ではSwagger UI・ReDoc・openapi.jsonを無効化
- `backend/core/limiter.py` — slowapi Limiterインスタンス（IPアドレスベース）
- `backend/core/config.py` — 環境変数設定（Supabase・Stripe・app_env）。app_envのデフォルトはproduction。developmentにするとSwagger UIが有効になる
- `backend/dependencies/auth.py` — 未使用（コードは保持）
- `backend/routers/analysis.py` — `/api/v1/analyze` エンドポイント。認証不要・全解析（PRNU含む）を全ユーザーに実行。レート制限：10回/分/IP
- `backend/routers/compare.py` — `/api/v1/compare` エンドポイント。認証不要。レート制限：5回/分/IP
- `backend/routers/stripe_router.py` — 未使用（コードは保持）
- `backend/services/exif_service.py` — Exifメタデータ解析・AIツール署名チェック。値が存在するフィールドのみ日本語ラベルで表示。メタデータなし→スコア0.6（カメラ情報の完全欠如はAI疑い）
- `backend/services/ela_service.py` — ELA解析（局所ホットスポット検出含む）
- `backend/services/texture_service.py` — 局所テクスチャ分散マップ。不自然に滑らかな領域を赤でハイライト（AI生成画像に特有）。分散閾値300・テクスチャ多様性（CV）でスコア補正（均一に滑らか＝AI・滑らかと詳細が混在＝本物写真）
- `backend/services/noise_service.py` — ノイズレベル解析。ノイズが少なすぎる領域を赤でハイライト（AI生成画像に特有）。ノイズ多様性（CV）でスコア補正（均一に低ノイズ＝AI・不均一＝本物写真）
- `backend/services/noise_consistency_service.py` — ノイズ整合性解析。不整合ブロックのみ赤でハイライト。偏差閾値0.7・係数1.5（AI画像の誤検出を減らすよう調整済み）。詳細は判定テキスト＋見方のみ表示（割合数値は非表示）
- `backend/services/dct_splicing_service.py` — DCTスプライシング検出。異常ブロックのみ赤でハイライト。z閾値2.5・係数2.0（AI画像の誤検出を減らすよう調整済み）。詳細は判定テキスト＋見方のみ表示（割合数値は非表示）
- `backend/services/prnu_service.py` — ノイズ残差マップ（最高精度の加工検出）。全ユーザーに実行。偏差閾値8.0・スコア＝ヒートマップ平均値×2.0（カメラ写真の誤検出を減らすよう調整済み）。詳細は判定テキスト＋見方のみ表示（割合数値は非表示）
- `backend/services/manipulation_service.py` — ノイズCoV検出。外れ値ブロックを赤でハイライト。外れ値閾値3σ・CoV重み0.3・外れ値重み0.7（AI画像の誤検出を減らすよう調整済み）。詳細は判定テキスト＋解説のみ表示（生数値は非表示）
- `backend/services/diff_service.py` — 2枚の画像の差分を赤でハイライト。label="diff"。詳細に差異率（%）と判定テキストを表示
- `backend/services/similarity_service.py` — SSIM＋パーセプチュアルハッシュで類似度をパーセント表示。label="similarity"。score=similarity/100で実際の類似度を反映
- `backend/requirements.txt` — 全依存パッケージ（slowapi==0.1.9追加済み）
- `supabase/schema.sql` — usage_logs・subscriptionsテーブル定義（Supabase SQLエディタで実行）
- AI判定スコア：3指標（Exif・テクスチャ・ノイズレベル）の平均
- 加工判定スコア：4指標（ノイズ整合性・DCT・PRNU・ノイズCoV）の平均。ELAはスコア計算対象外・参考表示のみ

## プロジェクト概要

AIが生成したフェイク画像・動画、および人為的に加工されたフェイク画像・動画を検出するWebサービス。
シンプルなUIで誰でも使えることを重視する。

## ビジネスモデル

- オープンソース（MITライセンス）でGitHubに公開
- 全機能を無料・無制限で提供してユーザーを増やす方向性（有料機能は一時停止）
- 将来的な収益化に備えてStripe・認証のコードは保持

## 技術スタック

| 役割 | 技術 |
|---|---|
| フロントエンド | React (TypeScript) |
| バックエンド | Python（FastAPI） |
| 認証・DB | Supabase |
| 決済 | Stripe（将来用） |

## 検出カテゴリ

| カテゴリ | 説明 |
|---|---|
| **AI生成検出** | GAN・拡散モデル等で生成された画像・動画の検出 |
| **人為的加工検出** | 実在の画像・動画をコラージュ・合成・編集した痕跡の検出 |

## 現在の機能（全ユーザー無料・無制限）

| 機能 |
|---|
| Exifメタデータ解析・AI署名チェック |
| ELA解析 |
| テクスチャ分析 |
| ノイズレベル解析 |
| ノイズ整合性解析 |
| DCTスプライシング検出 |
| ノイズ残差マップ |
| 2枚比較（差分・類似度） |

## 開発フェーズ

### フェーズ1（実装済み）

- 全解析機能（無制限・無料）
- ユーザー認証（Supabase）
- ダッシュボード（アカウント情報表示）

### フェーズ1（未実装）

- 解析履歴の保存
- PDFレポート出力

### フェーズ2（ユーザー獲得後）

- DeepFake動画検出（FaceForensics++）
- 動画解析（FFmpeg）
- 外部API連携（Hive API / Azure AI）
- 一括処理
- 収益化再検討（有料プラン復活）
- 広告追加（忍者AdMax等・ユーザーの邪魔にならない配置）
- API外部提供（APIキー認証・APIキー単位のレート制限）

## デプロイ環境

- **本番URL**: https://fakescan.karineffort.com
- **VPS OS**: Rocky Linux / Webサーバー: Apache
- **デプロイ先**: `/var/www/fakescan/`
- **フロントエンド静的ファイル**: `/var/www/fakescan/build/`
- **バックエンド**: `/var/www/fakescan/backend/`
- **systemdサービス名**: `fakescan.service`（gunicorn + uvicorn worker、ポート127.0.0.1:8000）
- **Apacheリバースプロキシ**: `/api/*` → gunicorn、静的ファイルはDocumentRootから配信
- **SSL**: Let's Encrypt（certbot）
- **フロントエンドビルド時の必須環境変数**（`/var/www/fakescan/.env.production`）:
  - `REACT_APP_API_URL=https://fakescan.karineffort.com/api/v1`
  - `REACT_APP_SUPABASE_URL`
  - `REACT_APP_SUPABASE_ANON_KEY`
- **バックエンド環境変数**（`/var/www/fakescan/backend/.env`）: `APP_ENV` / `ALLOWED_ORIGINS` / `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY`
- **更新デプロイ手順**:
  1. `git pull`
  2. フロントエンド変更時: `npm run build`
  3. バックエンド変更時: `sudo systemctl restart fakescan`

## ローカルドキュメント（gitignore対象・追跡外）

- `docs/zenn_article.md` — Zenn投稿用記事ドラフト（frontmatter付き・published: false）
- `docs/document.md` — 技術ドキュメント（アーキテクチャ・APIリファレンス・セットアップ・デプロイ手順）
- `.gitignore` に `/docs` を追加済み

## ライセンス

MIT License
