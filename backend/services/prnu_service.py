import io
import base64
import numpy as np
from PIL import Image, ImageFilter
from .base import get_label, error_result


def _noise_residual(gray: np.ndarray) -> np.ndarray:
    img_pil = Image.fromarray(gray.astype(np.uint8))
    smoothed = np.array(img_pil.filter(ImageFilter.GaussianBlur(radius=2)), dtype=float)
    return gray - smoothed


def _inconsistency_map(noise: np.ndarray, block: int = 32) -> np.ndarray:
    h, w = noise.shape
    heatmap = np.zeros((h, w), dtype=float)

    stds = []
    coords = []
    for y in range(0, h - block, block):
        for x in range(0, w - block, block):
            stds.append(float(np.std(noise[y:y + block, x:x + block])))
            coords.append((y, x))

    if not stds:
        return heatmap

    stds_arr = np.array(stds)
    median = float(np.median(stds_arr))
    mad = float(np.median(np.abs(stds_arr - median))) + 1e-8

    for i, (y, x) in enumerate(coords):
        deviation = abs(stds_arr[i] - median) / mad
        heatmap[y:y + block, x:x + block] = min(deviation / 5.0, 1.0)

    return heatmap


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img, dtype=float)
        gray = np.mean(arr, axis=2)

        noise = _noise_residual(gray)
        heatmap = _inconsistency_map(noise)

        anomaly_ratio = float(np.mean(heatmap > 0.5))
        top10 = np.sort(heatmap.flatten())[-max(1, len(heatmap.flatten()) // 10):]
        score = min(float(np.mean(top10)), 1.0)

        # オーバーレイ画像生成（赤でハイライト）
        original = np.array(img)
        red = np.zeros_like(original)
        red[:, :, 0] = 255
        alpha = heatmap[:, :, np.newaxis] * 0.7
        overlay = np.clip(original * (1 - alpha) + red * alpha, 0, 255).astype(np.uint8)

        out = io.BytesIO()
        Image.fromarray(overlay).save(out, format="PNG")
        img_b64 = base64.b64encode(out.getvalue()).decode()

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "anomaly_ratio": round(anomaly_ratio, 4),
                "note": "赤い箇所がノイズパターンの不整合領域（合成・切り貼りの可能性）",
            },
            "image": f"data:image/png;base64,{img_b64}",
        }
    except Exception as e:
        return error_result(str(e))
