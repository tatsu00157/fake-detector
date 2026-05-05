import io
import numpy as np
from PIL import Image
from .base import get_label, error_result


def _block_noise(patch: np.ndarray) -> float:
    diff_h = np.abs(np.diff(patch, axis=0))
    diff_v = np.abs(np.diff(patch, axis=1))
    return float((np.mean(diff_h) + np.mean(diff_v)) / 2)


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img, dtype=float)
        gray = np.mean(arr, axis=2)

        block = 32
        h, w = gray.shape
        noises = []
        for y in range(0, h - block, block):
            for x in range(0, w - block, block):
                patch = gray[y:y + block, x:x + block]
                noises.append(_block_noise(patch))

        if len(noises) < 4:
            return {"score": 0.0, "label": "clean", "details": {"note": "画像が小さすぎます"}, "image": None}

        noises = np.array(noises)
        mean_noise = float(np.mean(noises))
        std_noise = float(np.std(noises))
        cov = std_noise / (mean_noise + 1e-8)

        # 外れ値ブロック（ノイズが平均±2σを超える）の割合
        outlier_ratio = float(np.sum(np.abs(noises - mean_noise) > 2 * std_noise) / len(noises))

        # CoV > 1.0 で強い不整合、outlier_ratio > 0.1 で怪しいブロックが多い
        score = min((cov / 1.2 * 0.7) + (outlier_ratio / 0.15 * 0.3), 1.0)

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "noise_mean": round(mean_noise, 3),
                "noise_std": round(std_noise, 3),
                "noise_cov": round(cov, 4),
                "outlier_blocks": round(outlier_ratio, 4),
                "block_count": len(noises),
                "note": "ノイズ分布の不整合は合成・切り貼りの痕跡です",
            },
            "image": None,
        }
    except Exception as e:
        return error_result(str(e))
