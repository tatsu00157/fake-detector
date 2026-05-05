# フェイク画像・動画検出サービス 設計書

## ルール

- **コードの修正は必ずユーザーに確認してから行う**
- **コードを修正したら必ずこのCLAUDE.mdを最新の状態に更新する**
- **CLAUDE.mdを更新したら必ずgit commit & pushをセットで行う**
- **APIキー・パスワード・個人情報などの機密情報は絶対にチャットに出力しない**

## 実装済み

### フロントエンド
- `src/App.tsx` — ヘッダー＋ホームページのシェル
- `src/App.css` — グローバルスタイル（ヘッダー・ホーム・アップロードゾーン）
- `src/components/Header.tsx` — ヘッダーコンポーネント
- `src/components/UploadZone.tsx` — ドラッグ＆ドロップ対応アップロードUI
- `src/pages/Home.tsx` — ホームページ（モード切替・アップロード・プレビュー）
- `tsconfig.json` — `target: es2020`、`moduleResolution: bundler` に修正済み
- `src/types/analysis.ts` — 解析結果の型定義
- `src/components/AnalysisCard.tsx` — 解析項目カード（スコアバー・詳細展開）
- `src/components/ResultsDashboard.tsx` — 解析結果一覧（総合判定・AI生成・人為的加工・情報）
- `src/api/client.ts` — バックエンドAPIクライアント
- `src/pages/Home.tsx` — 実APIと連携済み（ローディング・エラー表示あり）

### バックエンド
- `backend/main.py` — FastAPIアプリ本体
- `backend/core/config.py` — 環境変数設定
- `backend/routers/analysis.py` — `/api/v1/analyze` エンドポイント
- `backend/services/exif_service.py` — Exifメタデータ解析・AIツール署名チェック
- `backend/services/ela_service.py` — ELA解析（局所ホットスポット検出含む）
- `backend/services/fft_service.py` — 周波数解析（FFT）
- `backend/services/pixel_stats_service.py` — ピクセル統計解析（彩度シグナル削除済み・AI誤検知防止）
- `backend/services/face_service.py` — 顔検出
- `backend/services/ai_features_service.py` — エッジシャープネス・カラーパレット解析（アニメAI検出）
- `backend/services/prnu_service.py` — ノイズ残差マップ（PRNUベース）で合成・切り貼り箇所を可視化
- `backend/services/manipulation_service.py` — ノイズCoV検出（スコア計算には未使用）
- AI判定スコア：4指標（Exif・FFT・ピクセル統計・AIフィーチャー）の平均
- 加工判定スコア：2指標（ELA・PRNU）の平均
- 総合判定をAI生成スコアと加工スコアに分離

### フロントエンド（更新）
- `src/components/ResultsDashboard.tsx` — 表示カードをEXIF・ELA・PRNUの3枚に絞り込み。総合判定カード・FFT・ピクセル統計・AIフィーチャー・顔検出カード・セクションタイトルをすべて削除
- `src/types/analysis.ts` — `prnu` フィールド追加

## プロジェクト概要

AIが生成したフェイク画像・動画、および人為的に加工されたフェイク画像・動画を検出するWebサービス。
シンプルなUIで誰でも使えることを重視する。

## ビジネスモデル

- オープンソース（MITライセンス）でGitHubに公開
- 誰でも無料で使えるWebサービスとして公開し、一部の機能は月額料金で提供
- 決済：Stripe
- 収益化はフェーズ1から対応（Stripe + 認証 + 使用回数制限を初期実装）

## 技術スタック

| 役割 | 技術 |
|---|---|
| フロントエンド | React (TypeScript) |
| バックエンド | Python（FastAPI） |
| 決済 | Stripe |

## 検出カテゴリ

本サービスは以下2種類のフェイクを検出対象とする。

| カテゴリ | 説明 |
|---|---|
| **AI生成検出** | GAN・拡散モデル等で生成された画像・動画の検出 |
| **人為的加工検出** | 実在の画像・動画をコラージュ・合成・編集した痕跡の検出 |

## 機能設計

### UI基本方針

- 画像・動画をドラッグ＆ドロップでアップロード
- アップロードしたら全解析結果が一画面に表示される
- 解析項目を個別に選ぶUIにはしない

### 解析機能一覧

| 機能 | カテゴリ | 内容 | ツール |
|---|---|---|---|
| Exifメタデータ解析 | 両方 | 撮影情報・改ざん痕跡・AIツール署名の検出 | ExifTool |
| AIメタデータ署名チェック | AI生成 | SD・MidJourney・DALL-E等が埋め込むメタデータ検出 | ExifTool（Exif拡張） |
| ELA解析 | 人為的加工 | JPEG再圧縮アーティファクトによる編集箇所検出 | Pillow |
| 周波数解析（FFT） | AI生成 | GAN特有の周期ノイズ・グリッドパターン検出 | NumPy / OpenCV |
| ピクセル統計解析 | AI生成 | AI画像特有の輝度・色分布の偏りを数値化 | NumPy |
| クローンスタンプ検出 | 人為的加工 | 同一画像内のコピー&ペースト領域を検出 | OpenCV |
| 差分検出 | 両方 | 2枚の画像の違いをハイライト | OpenCV |
| 類似度比較 | 両方 | 2枚の画像の類似度を数値化 | imagehash, SSIM |
| 顔検出 | 両方 | 顔の有無・位置を検出 | OpenCV |
| 同一人物判定 | 両方 | 2枚の画像が同一人物かどうか判定 | face_recognition |
| ノイズ整合性解析 | 人為的加工 | 合成箇所のカメラセンサーノイズ不整合を検出 | NumPy |
| スプライシング検出 | 人為的加工 | 別ソース画像の合成痕跡をDCT解析で検出 | OpenCV |
| 照明・影の整合性 | 人為的加工 | 合成時の光源不一致を検出 | OpenCV |
| AI生成画像検出（精度高） | AI生成 | GAN・拡散モデル生成画像の高精度検出 | EfficientNet-B0（CIFAKE fine-tuned） |
| DeepFake検出 | AI生成 | 顔すり替え・改変の検出 | FaceForensics++ |
| 動画解析 | 両方 | 動画のメタデータ解析・フレーム単位検出 | FFmpeg |
| 高精度検出 | 両方 | 外部APIによる高精度解析 | Hive API / Azure AI |

### 無料/有料プラン

| 機能 | 無料 | 有料 | サーバー負荷 |
|---|---|---|---|
| Exifメタデータ解析 | ✅ | ✅ | 極低 |
| AIメタデータ署名チェック | ✅ | ✅ | 極低 |
| ELA解析 | ✅ | ✅ | 低 |
| 周波数解析（FFT） | ✅ | ✅ | 低 |
| ピクセル統計解析 | ✅ | ✅ | 低 |
| クローンスタンプ検出 | ✅ | ✅ | 低 |
| 差分検出 | ✅ | ✅ | 低 |
| 類似度比較 | ✅ | ✅ | 低 |
| 顔検出 | ✅ | ✅ | 低 |
| 同一人物判定 | ❌ | ✅ | 中 |
| ノイズ整合性解析 | ❌ | ✅ | 中 |
| スプライシング検出 | ❌ | ✅ | 中 |
| 照明・影の整合性 | ❌ | ✅ | 中 |
| AI生成画像検出（精度高） | ❌ | ✅ | 中 |
| DeepFake検出 | ❌ | ✅ | 高 |
| 動画解析 | ❌ | ✅ | 高 |
| 高精度検出（外部API） | ❌ | ✅ | 低（外部コスト） |
| PDFレポート出力 | ❌ | ✅ | 低 |
| 履歴保存 | 7日間 | 無制限 | — |
| 一括処理 | ❌ | ✅ | 高 |
| 1日の利用回数 | 10回 | 無制限 | — |

### コスト設計方針

- 無料枠はサーバー内で完結する処理のみ（外部API通信なし）
- 外部APIは有料プランのみで使用（コスト管理）
- 動画解析・DeepFake検出はサーバー負荷が高いため有料限定
- 収益化はフェーズ1から対応し、有料機能の目玉（AI生成検出・同一人物判定等）も初期リリースに含める

## 開発フェーズ

### フェーズ1（初期リリース）

軽量で動くものから実装しつつ、収益化インフラも同時に構築する。

**解析機能（無料）:**
- Exifメタデータ解析 + AIメタデータ署名チェック
- ELA解析
- 周波数解析（FFT）
- ピクセル統計解析
- クローンスタンプ検出
- 差分検出
- 類似度比較
- 顔検出

**解析機能（有料）:**
- 同一人物判定（face_recognition）
- ノイズ整合性解析
- スプライシング検出
- 照明・影の整合性
- AI生成画像検出（EfficientNet-B0）

**インフラ:**
- ユーザー認証
- Stripe課金（月額サブスクリプション）
- 使用回数制限（無料: 1日10回 / 有料: 無制限）

### フェーズ2（収益化後・サーバーアップグレード後）

- DeepFake動画検出（FaceForensics++）
- 動画解析（FFmpeg）
- 外部API連携（Hive API / Azure AI）
- 一括処理
- PDFレポート出力

## ライセンス

MIT License
