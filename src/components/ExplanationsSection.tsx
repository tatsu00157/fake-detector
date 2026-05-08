import React from 'react';

const EXPLANATIONS = [
  {
    category: 'AI生成検出',
    items: [
      {
        label: 'メタデータ解析',
        desc: 'Exifデータを解析し、AI生成ツール（Stable Diffusion・DALL-Eなど）の署名や撮影機器情報の欠如を検出します。',
        how: '本物の写真にはカメラ機種・撮影設定などのExif情報が含まれます。これらが存在しない、またはAIツールのソフトウェア名が記録されている場合にスコアが上がります。マップ表示はありません。',
      },
      {
        label: 'テクスチャ分析',
        desc: 'AI生成画像に特有の「滑らかすぎる」テクスチャパターンを検出します。',
        how: '赤くハイライトされた領域が、局所的に不自然に均一なテクスチャを持つ箇所です。人間の肌・布・背景などがAIによって過度に滑らかに生成されると検出されます。赤が多いほどAI生成の可能性が高まります。',
      },
      {
        label: 'ノイズレベル解析',
        desc: '本物の写真が持つ自然なノイズ（粒状感）の有無を検査します。',
        how: '赤くハイライトされた領域がノイズが少なすぎる箇所です。本物の写真には撮影センサー由来のランダムなノイズが乗りますが、AI生成画像はこのノイズが極端に少ない傾向があります。',
      },
    ],
  },
  {
    category: '加工検出',
    items: [
      {
        label: 'ノイズ整合性解析',
        desc: '画像全体のノイズパターンが均一かどうかを検査します。',
        how: '画像を小ブロックに分割し、各ブロックのノイズ特性を比較します。赤いブロックは周囲と異なるノイズパターンを持っており、別の画像から切り取って貼り付けられた可能性を示します。',
      },
      {
        label: 'DCTスプライシング検出',
        desc: 'JPEG圧縮の周波数成分（DCT係数）の統計的パターンを解析して合成痕跡を検出します。',
        how: '同一カメラ・同一設定で撮影された画像はDCT係数の分布が均一になります。赤いブロックはこの分布から外れた異常領域で、別ソースからの合成・切り貼りが疑われます。',
      },
      {
        label: 'ノイズ残差マップ',
        desc: '画像からノイズ残差を抽出し、撮影センサーの固有パターン（PRNU）の整合性を解析します。',
        how: '同じカメラで撮影した画像は固有のノイズ指紋を持ちます。赤くハイライトされた箇所はこの指紋と一致しない領域で、別の画像から合成・切り貼りされた可能性が最も高い箇所です。4つの加工検出の中で最も精度が高い指標です。',
      },
      {
        label: 'ノイズCoV（ノイズ変動係数）',
        desc: '画像をブロックに分割し、各ブロックのノイズ量のばらつきを検査します。',
        how: 'ノイズの変動係数（標準偏差÷平均）と外れ値ブロック率からスコアを算出します。合成・切り貼りされた箇所はノイズの統計特性が周囲と異なるため赤くハイライトされます。',
      },
      {
        label: 'ELA解析（Error Level Analysis）※参考表示',
        desc: 'JPEG圧縮の誤差レベルを可視化し、加工・編集された箇所を検出します。PNG・再圧縮済みJPEGでは信頼性が低いためスコア計算の対象外です。',
        how: '同じ条件で再圧縮したとき、加工された箇所は周囲と異なる誤差レベルを示します。マップ上で明るく光っている箇所が加工疑いの領域です。',
      },
    ],
  },
  {
    category: 'スコアの見方',
    items: [
      {
        label: '安全（0〜30%）',
        desc: 'AI生成・加工の痕跡がほとんど検出されていません。',
        how: '',
      },
      {
        label: '要注意（30〜60%）',
        desc: '一部に疑わしい特徴が検出されました。断定はできませんが注意が必要です。',
        how: '',
      },
      {
        label: '疑わしい（60〜100%）',
        desc: '強いAI生成または加工の痕跡が検出されました。複数の指標を組み合わせて判断してください。',
        how: '',
      },
    ],
  },
];

export default function ExplanationsSection() {
  return (
    <div className="explanations">
      <h2 className="explanations__title">解析指標について</h2>
      {EXPLANATIONS.map((group) => (
        <div key={group.category} className="explanations__group">
          <h3 className="explanations__group-title">{group.category}</h3>
          <div className="explanations__cards">
            {group.items.map((item) => (
              <div key={item.label} className="explanation-card">
                <p className="explanation-card__label">{item.label}</p>
                <p className="explanation-card__desc">{item.desc}</p>
                {item.how && <p className="explanation-card__how">{item.how}</p>}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
