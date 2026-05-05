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


def analyze(image_bytes: bytes) -> dict:
    try:
        arr = np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"), dtype=float)
        channels = {"red": arr[:, :, 0].flatten(), "green": arr[:, :, 1].flatten(), "blue": arr[:, :, 2].flatten()}
        stats = {name: _channel_stats(ch) for name, ch in channels.items()}

        suspicious_signals = sum(
            1 for ch in stats.values()
            if ch["entropy"] > 7.5 and abs(ch["skewness"]) < 0.3
        )
        score = min(suspicious_signals / 3.0 * 0.6, 0.6)

        r, g, b = channels["red"], channels["green"], channels["blue"]
        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "channels": stats,
                "color_correlation": {
                    "rg": round(float(np.corrcoef(r, g)[0, 1]), 4),
                    "rb": round(float(np.corrcoef(r, b)[0, 1]), 4),
                    "gb": round(float(np.corrcoef(g, b)[0, 1]), 4),
                },
                "suspicious_signals": suspicious_signals,
                "note": "AI画像は各チャンネルの統計が自然画像と異なる傾向があります",
            },
            "image": None,
        }
    except Exception as e:
        return error_result(str(e))
