# フェイク画像・動画検出サービス 設計書

## ルール

- **コードの修正は「内容を説明→ユーザーの承認を待つ→修正実行」の順で行う。説明後は必ずユーザーの返答を待つ**
- **コードを修正したら必ずこのCLAUDE.mdを最新の状態に更新する**
- **CLAUDE.mdを更新したら必ずgit commit & pushをセットで行う**
- **APIキー・パスワード・個人情報などの機密情報は絶対にチャットに出力しない**

## 実装済み

### フロントエンド
- `src/App.tsx` — React Router導入。/ルートのみ。認証関連ルートはUI非公開（コードは保持）
- `src/App.css` — グローバルスタイル（ヘッダー・ホーム・アップロードゾーンなど）
- `src/components/ScrollToTop.tsx` — ルート変更時に自動でページ最上部にスムーズスクロール
- `src/components/Header.tsx` — ロゴ（FakeScan・lang="en"）はホームへのリンク。ロゴ左にピンク（#f472b6）の虫眼鏡SVGアイコン。右側にホームリンク。ロゴ・ホームリンクはクリック時にscrollTo(0,0)
- `src/components/Footer.tsx` — フッター。ロゴとコピーライトにlang="en"設定。プライバシーポリシー・利用規約リンクのみ（お問い合わせリンクは削除）
- `src/components/UploadZone.tsx` — ドラッグ＆ドロップ対応アップロードUI（日本語テキスト）
- `src/components/AnalysisCard.tsx` — 解析項目カード（スコアバー・詳細展開・画像表示）
- `src/components/ResultsDashboard.tsx` — AI生成検出・加工検出をタブUI（メタデータ・テクスチャ・ノイズ等）で切り替え表示。セクションごとの総合スコアバッジ。タブに判定カラードット表示。結果上部に参考情報である旨の免責注意書き表示
- `src/components/ExplanationsSection.tsx` — 解析指標の説明・マップの見方・スコア基準。Home.tsxで常時表示
- `src/types/analysis.ts` — 解析結果の型定義。noise_consistency・dct_splicing・prnu?
- `src/lib/supabase.ts` — Supabaseクライアント
- `src/context/AuthContext.tsx` — 認証状態管理（ログイン・ログアウト・セッション）
- `src/api/client.ts` — 認証なし・シンプルなfetch。analyzeImage・compareImagesのみ
- `src/pages/Home.tsx` — ホームページ。利用制限なし・無制限。アップロード後は左にアップロードゾーン・右にプレビューを横並び表示。「解析する」「比較する」ボタンを押して解析開始。解析中はプレビュー上に走査線アニメーションとドットインジケーター表示。スマホは縦並びにフォールバック
- `src/pages/PrivacyPolicy.tsx` — プライバシーポリシーページ（/privacy）
- `src/pages/Terms.tsx` — 利用規約ページ（/terms）
- `src/pages/Login.tsx` — ログインページ。下部に新規登録へのリンク
- `src/pages/Signup.tsx` — 新規登録ページ。パスワード表示切替・要件リアルタイム表示（8文字以上・英字・数字・記号）・パスワード確認欄
- `src/pages/Dashboard.tsx` — ダッシュボードページ。ログイン中のメールアドレスを表示
- `public/index.html` — lang="ja"設定・タイトルをFakeScanに変更
- ブランドカラー：ピンク（`#f472b6`）を登録系CTAボタンに使用

### バックエンド
- `backend/main.py` — FastAPIアプリ本体
- `backend/core/config.py` — 環境変数設定（Supabase・Stripe）
- `backend/dependencies/auth.py` — 未使用（コードは保持）
- `backend/routers/analysis.py` — `/api/v1/analyze` エンドポイント。認証不要・全解析（PRNU含む）を全ユーザーに実行
- `backend/routers/compare.py` — `/api/v1/compare` エンドポイント。認証不要
- `backend/routers/stripe_router.py` — 未使用（コードは保持）
- `backend/services/exif_service.py` — Exifメタデータ解析・AIツール署名チェック。値が存在するフィールドのみ日本語ラベルで表示。メタデータなし→スコア0.6（カメラ情報の完全欠如はAI疑い）
- `backend/services/ela_service.py` — ELA解析（局所ホットスポット検出含む）
- `backend/services/texture_service.py` — 局所テクスチャ分散マップ。不自然に滑らかな領域を赤でハイライト（AI生成画像に特有）
- `backend/services/noise_service.py` — ノイズレベル解析。ノイズが少なすぎる領域を赤でハイライト（AI生成画像に特有）
- `backend/services/noise_consistency_service.py` — ノイズ整合性解析。不整合ブロックのみ赤でハイライト。偏差閾値0.7・係数1.5（AI画像の誤検出を減らすよう調整済み）。詳細は判定テキスト＋見方のみ表示（割合数値は非表示）
- `backend/services/dct_splicing_service.py` — DCTスプライシング検出。異常ブロックのみ赤でハイライト。z閾値2.5・係数2.0（AI画像の誤検出を減らすよう調整済み）。詳細は判定テキスト＋見方のみ表示（割合数値は非表示）
- `backend/services/prnu_service.py` — ノイズ残差マップ（最高精度の加工検出）。全ユーザーに実行。スコア＝ヒートマップ平均値×3.0で視覚（赤の量）とスコアが一致。詳細は判定テキスト＋見方のみ表示（割合数値は非表示）
- `backend/services/manipulation_service.py` — ノイズCoV検出。外れ値ブロックを赤でハイライト。外れ値閾値3σ・CoV重み0.3・外れ値重み0.7（AI画像の誤検出を減らすよう調整済み）。詳細は判定テキスト＋解説のみ表示（生数値は非表示）
- `backend/services/diff_service.py` — 2枚の画像の差分を赤でハイライト
- `backend/services/similarity_service.py` — SSIM＋パーセプチュアルハッシュで類似度をパーセント表示
- `backend/requirements.txt` — 全依存パッケージ
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

## ライセンス

MIT License
