# フェイク画像・動画検出サービス 設計書

## ルール

- **コードの修正は「内容を説明→ユーザーの承認を待つ→修正実行」の順で行う。説明後は必ずユーザーの返答を待つ**
- **コードを修正したら必ずこのCLAUDE.mdを最新の状態に更新する**
- **CLAUDE.mdを更新したら必ずgit commit & pushをセットで行う**
- **APIキー・パスワード・個人情報などの機密情報は絶対にチャットに出力しない**

## 実装済み

### フロントエンド
- `src/App.tsx` — React Router導入。全ページ公開（認証はアップロード時にチェック）。/・/login・/signup・/pricing・/dashboardルート
- `src/App.css` — グローバルスタイル（ヘッダー・ホーム・アップロードゾーン・ダッシュボード・料金プランなど）
- `src/components/Header.tsx` — ロゴ（FakeScan・lang="en"）はホームへのリンク。全ユーザーに「料金プラン」リンク。未ログイン時は「ログイン」「新規登録」。ログイン中は「ダッシュボード」「ログアウト」
- `src/components/Footer.tsx` — フッター。ロゴとコピーライトにlang="en"設定
- `src/components/UploadZone.tsx` — ドラッグ＆ドロップ対応アップロードUI（日本語テキスト）
- `src/components/AnalysisCard.tsx` — 解析項目カード（スコアバー・詳細展開・画像表示）
- `src/components/ResultsDashboard.tsx` — AI生成検出（EXIF・テクスチャ・ノイズレベル）と加工検出（ELA・ノイズ整合性・DCT・PRNUはプレミアムのみ）でセクション分け
- `src/types/analysis.ts` — 解析結果の型定義。noise_consistency・dct_splicing（無料）・prnu?（プレミアム）
- `src/lib/supabase.ts` — Supabaseクライアント
- `src/context/AuthContext.tsx` — 認証状態管理（ログイン・ログアウト・セッション）
- `src/api/client.ts` — 全APIリクエストにSupabase JWTを付与。createCheckoutSession・createPortalSession追加
- `src/pages/Home.tsx` — ホームページ。ゲスト3回/日・無料登録10回/日の利用制限。上限時はページ内に登録促進バナーを表示。2枚比較モードは2枚目アップロード後に自動で比較実行
- `src/pages/Login.tsx` — ログインページ。下部に新規登録へのリンク
- `src/pages/Signup.tsx` — 新規登録ページ。パスワード表示切替・要件リアルタイム表示（8文字以上・英字・数字・記号）・パスワード確認欄
- `src/pages/Pricing.tsx` — 料金プランページ（無料・プレミアム980円/月）。プランカード＋機能比較表。Stripe Checkoutへリダイレクト。ログイン中はSubscriptionsテーブルを参照して現在のプランを表示。機能比較表は無料・有料共通機能を上に、プレミアム限定（ノイズ残差マップ・PDFレポート・解析履歴）を下に配置
- `src/pages/Dashboard.tsx` — ダッシュボードページ。現在のプラン表示。プレミアムなら「プランを管理する・解約する」（Stripeポータル）、無料なら「アップグレード」ボタン
- `public/index.html` — lang="ja"設定・タイトルをFakeScanに変更
- ブランドカラー：ピンク（`#f472b6`）を登録系CTAボタンに使用

### バックエンド
- `backend/main.py` — FastAPIアプリ本体
- `backend/core/config.py` — 環境変数設定（Supabase・Stripe）
- `backend/dependencies/auth.py` — JWT検証・無料利用回数チェック（1日10回）・プレミアム判定（_is_premium）・require_auth（Stripeエンドポイント用）
- `backend/routers/analysis.py` — `/api/v1/analyze` エンドポイント。無料：exif・ela・fft・pixel_stats・manipulation・face・ai_features・texture・noise・noise_consistency・dct_splicing。プレミアム追加：prnu
- `backend/routers/compare.py` — `/api/v1/compare` エンドポイント（2ファイル受け取り）
- `backend/routers/stripe_router.py` — Stripe Checkout・ポータル・Webhookエンドポイント。subscription_dataにuser_idメタデータを付与
- `backend/services/exif_service.py` — Exifメタデータ解析・AIツール署名チェック。値が存在するフィールドのみ日本語ラベルで表示
- `backend/services/ela_service.py` — ELA解析（局所ホットスポット検出含む）
- `backend/services/fft_service.py` — 周波数解析（FFT）
- `backend/services/pixel_stats_service.py` — ピクセル統計解析
- `backend/services/face_service.py` — 顔検出
- `backend/services/ai_features_service.py` — エッジシャープネス・カラーパレット解析
- `backend/services/texture_service.py` — 局所テクスチャ分散マップ。不自然に滑らかな領域を赤でハイライト（AI生成画像に特有）
- `backend/services/noise_service.py` — ノイズレベル解析。ノイズが少なすぎる領域を赤でハイライト（AI生成画像に特有）
- `backend/services/noise_consistency_service.py` — ノイズ整合性解析。不整合ブロックのみ赤でハイライト。無料機能
- `backend/services/dct_splicing_service.py` — DCTスプライシング検出。異常ブロックのみ赤でハイライト。無料機能
- `backend/services/prnu_service.py` — ノイズ残差マップ（最高精度の加工検出）。プレミアムのみ
- `backend/services/manipulation_service.py` — ノイズCoV検出（スコア計算には未使用）
- `backend/services/diff_service.py` — 2枚の画像の差分を赤でハイライト
- `backend/services/similarity_service.py` — SSIM＋パーセプチュアルハッシュで類似度をパーセント表示
- `backend/requirements.txt` — 全依存パッケージ（transformers・torchはai_detection削除後も残存）
- `supabase/schema.sql` — usage_logs・subscriptionsテーブル定義（Supabase SQLエディタで実行）
- AI判定スコア：3指標（Exif・テクスチャ・ノイズレベル）の平均
- 加工判定スコア：3指標（ELA・ノイズ整合性・DCT）の平均
- ゲスト：3回/日（localStorage管理）、無料登録：10回/日（Supabase管理）、有料：無制限

## プロジェクト概要

AIが生成したフェイク画像・動画、および人為的に加工されたフェイク画像・動画を検出するWebサービス。
シンプルなUIで誰でも使えることを重視する。

## ビジネスモデル

- オープンソース（MITライセンス）でGitHubに公開
- 誰でも無料で使えるWebサービスとして公開し、一部の機能は月額料金で提供
- 決済：Stripe（月額980円）
- 収益化はフェーズ1から対応（Stripe + 認証 + 使用回数制限を初期実装）

## 技術スタック

| 役割 | 技術 |
|---|---|
| フロントエンド | React (TypeScript) |
| バックエンド | Python（FastAPI） |
| 認証・DB | Supabase |
| 決済 | Stripe |

## 検出カテゴリ

| カテゴリ | 説明 |
|---|---|
| **AI生成検出** | GAN・拡散モデル等で生成された画像・動画の検出 |
| **人為的加工検出** | 実在の画像・動画をコラージュ・合成・編集した痕跡の検出 |

## 現在の無料/有料機能

| 機能 | 無料 | 有料 |
|---|---|---|
| Exifメタデータ解析・AI署名チェック | ✅ | ✅ |
| ELA解析 | ✅ | ✅ |
| テクスチャ分析 | ✅ | ✅ |
| ノイズレベル解析 | ✅ | ✅ |
| ノイズ整合性解析 | ✅ | ✅ |
| DCTスプライシング検出 | ✅ | ✅ |
| 2枚比較（差分・類似度） | ✅ | ✅ |
| ノイズ残差マップ（高精度） | ❌ | ✅ |
| PDFレポート出力 | ❌ | ✅（未実装） |
| 解析履歴の保存 | ❌ | ✅（未実装） |
| 1日の利用回数 | 3回（ゲスト）/10回（登録） | 無制限 |

## 開発フェーズ

### フェーズ1（実装済み）

- 全無料解析機能
- ノイズ残差マップ（プレミアム）
- ユーザー認証（Supabase）
- Stripe課金（月額サブスクリプション）
- 使用回数制限
- ダッシュボード（プラン管理・解約）

### フェーズ1（未実装）

- 解析履歴の保存
- PDFレポート出力

### フェーズ2（収益化後・サーバーアップグレード後）

- DeepFake動画検出（FaceForensics++）
- 動画解析（FFmpeg）
- 外部API連携（Hive API / Azure AI）
- 一括処理

## ライセンス

MIT License
