import io
import numpy as np
from PIL import Image
from .base import get_label, error_result


def _histogram_gaps(channel: np.ndarray) -> float:
    """ヒストグラムのギャップ検出。コントラスト・レベル調整で空白が生まれる。"""
    hist, _ = np.histogram(channel, bins=256, range=(0, 256))
    # 中間域（端の黒潰れ・白飛びを除く）のゼロビン数を数える
    mid = hist[10:246]
    gap_count = int(np.sum(mid == 0))
    return gap_count / len(mid)


def _clipping(channel: np.ndarray) -> float:
    """クリッピング検出。明るさ調整の過度な操作でヒストグラム端に異常集中が出る。"""
    total = len(channel)
    black_clip = float(np.sum(channel <= 2)) / total
    white_clip = float(np.sum(channel >= 253)) / total
    return max(black_clip, white_clip)


def _saturation_anomaly(arr: np.ndarray) -> float:
    """彩度の不自然な高さ。スマホフィルターによる彩度ブーストを検出。"""
    r = arr[:, :, 0] / 255.0
    g = arr[:, :, 1] / 255.0
    b = arr[:, :, 2] / 255.0
    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    sat = np.where(maxc > 0, (maxc - minc) / maxc, 0.0)
    mean_sat = float(np.mean(sat))
    # 彩度の分布の均一性（フィルターをかけると均一に高くなる）
    sat_std = float(np.std(sat))
    # 高彩度かつ均一 = フィルター処理の可能性
    if mean_sat > 0.5 and sat_std < 0.25:
        return mean_sat
    return 0.0


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img, dtype=float)

        r, g, b = arr[:, :, 0].flatten(), arr[:, :, 1].flatten(), arr[:, :, 2].flatten()

        gap_r = _histogram_gaps(r)
        gap_g = _histogram_gaps(g)
        gap_b = _histogram_gaps(b)
        gap_score = float(np.mean([gap_r, gap_g, gap_b]))

        clip_r = _clipping(r)
        clip_g = _clipping(g)
        clip_b = _clipping(b)
        clip_score = float(np.mean([clip_r, clip_g, clip_b]))

        sat_score = _saturation_anomaly(arr)

        # 各スコアを統合
        gap_suspicious  = gap_score > 0.05   # 5%以上のギャップ
        clip_suspicious = clip_score > 0.03  # 3%以上のクリッピング
        sat_suspicious  = sat_score > 0.55   # 高彩度かつ均一

        signal_count = (1 if gap_suspicious else 0) + (1 if clip_suspicious else 0) + (1 if sat_suspicious else 0)
        score = min(signal_count / 3.0, 1.0)

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "histogram_gap_ratio": round(gap_score, 4),
                "clipping_ratio": round(clip_score, 4),
                "saturation_anomaly": round(sat_score, 4),
                "note": "ヒストグラムのギャップ・クリッピング・彩度の不自然さで加工を検出します",
            },
            "image": None,
        }
    except Exception as e:
        return error_result(str(e))
