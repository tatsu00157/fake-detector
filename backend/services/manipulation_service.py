import io
import numpy as np
from PIL import Image
from .base import get_label, error_result


def _histogram_gaps(channel: np.ndarray) -> float:
    """ヒストグラムのギャップ検出。レベル補正・コントラスト調整で空白ビンが生まれる。
    実際のカメラはこのギャップを作らないため、編集の痕跡として有効。"""
    hist, _ = np.histogram(channel, bins=256, range=(0, 256))
    # 端の黒潰れ・白飛び領域を除いた中間域のゼロビン数
    mid = hist[10:246]
    gap_count = int(np.sum(mid == 0))
    return gap_count / len(mid)


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img, dtype=float)

        r, g, b = arr[:, :, 0].flatten(), arr[:, :, 1].flatten(), arr[:, :, 2].flatten()

        gap_r = _histogram_gaps(r)
        gap_g = _histogram_gaps(g)
        gap_b = _histogram_gaps(b)
        gap_score = float(np.mean([gap_r, gap_g, gap_b]))

        score = min(gap_score / 0.1, 1.0)  # 10%ギャップで最大スコア

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "histogram_gap_ratio": round(gap_score, 4),
                "gap_per_channel": {
                    "red":   round(gap_r, 4),
                    "green": round(gap_g, 4),
                    "blue":  round(gap_b, 4),
                },
                "note": "ヒストグラムの空白ビンはレベル補正・コントラスト調整の痕跡です",
            },
            "image": None,
        }
    except Exception as e:
        return error_result(str(e))
