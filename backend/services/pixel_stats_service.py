import io
import numpy as np
from PIL import Image
from .base import get_label, error_result


def _channel_stats(flat: np.ndarray) -> dict:
    mean = float(np.mean(flat))
    std = float(np.std(flat)) + 1e-8
    centered = flat - mean
    skewness = float(np.mean(centered ** 3) / std ** 3)
    kurt = float(np.mean(centered ** 4) / std ** 4 - 3)
    hist, _ = np.histogram(flat, bins=256, range=(0, 256))
    hist_norm = hist / (hist.sum() + 1e-8)
    entropy = float(-np.sum(hist_norm[hist_norm > 0] * np.log2(hist_norm[hist_norm > 0] + 1e-8)))
    return {
        "mean": round(mean, 2),
        "std": round(std, 2),
        "skewness": round(skewness, 4),
        "kurtosis": round(kurt, 4),
        "entropy": round(entropy, 4),
    }


def _noise_level(arr: np.ndarray) -> float:
    gray = np.mean(arr, axis=2)
    block = 8
    h, w = gray.shape
    stds = []
    for y in range(0, h - block, block):
        for x in range(0, w - block, block):
            patch = gray[y:y + block, x:x + block]
            m = np.mean(patch)
            if 20 < m < 235:
                stds.append(float(np.std(patch)))
    if not stds:
        return 5.0
    stds_sorted = sorted(stds)
    return float(np.mean(stds_sorted[:max(1, len(stds_sorted) // 4)]))


def _saturation(arr: np.ndarray) -> float:
    r = arr[:, :, 0] / 255.0
    g = arr[:, :, 1] / 255.0
    b = arr[:, :, 2] / 255.0
    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    sat = np.where(maxc > 0, (maxc - minc) / maxc, 0.0)
    return float(np.mean(sat))


def _color_flatness(arr: np.ndarray) -> float:
    block = 16
    h, w = arr.shape[:2]
    local_vars = [
        float(np.var(arr[y:y + block, x:x + block]))
        for y in range(0, h - block, block)
        for x in range(0, w - block, block)
    ]
    return float(np.mean(local_vars)) if local_vars else 1000.0


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img, dtype=float)

        channels = {
            "red":   arr[:, :, 0].flatten(),
            "green": arr[:, :, 1].flatten(),
            "blue":  arr[:, :, 2].flatten(),
        }
        stats = {name: _channel_stats(ch) for name, ch in channels.items()}

        noise    = _noise_level(arr)
        flatness = _color_flatness(arr)

        stat_suspicious  = sum(
            1 for ch in stats.values()
            if ch["entropy"] > 7.0 and abs(ch["skewness"]) < 0.5
        )
        noise_suspicious = noise < 2.5    # 実写は通常2以上、AI画像は不自然に低い
        flat_suspicious  = flatness < 800 # アニメAIはフラットな塗りで局所分散が小さい

        signal_count = stat_suspicious + (1 if noise_suspicious else 0) + (1 if flat_suspicious else 0)
        score = min(signal_count / 4.0, 1.0)

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "noise_level": round(noise, 3),
                "color_flatness": round(flatness, 1),
                "suspicious_signals": signal_count,
                "note": "ノイズが低い・色がフラットな場合はAI生成の可能性があります",
            },
            "image": None,
        }
    except Exception as e:
        return error_result(str(e))
