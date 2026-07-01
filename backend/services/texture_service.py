import io
import base64
import numpy as np
import cv2
from PIL import Image
from .base import get_label, error_result

BLOCK = 8
HEATMAP_THRESHOLD = 0.5  # smoothness > 0.5 = variance < 10 = 不自然に滑らか


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img, dtype=float)
        gray = np.mean(arr, axis=2)

        h, w = gray.shape
        smoothness = np.zeros((h, w), dtype=float)

        for y in range(0, h - BLOCK, BLOCK):
            for x in range(0, w - BLOCK, BLOCK):
                patch = gray[y:y + BLOCK, x:x + BLOCK]
                var = float(np.var(patch))
                smoothness[y:y + BLOCK, x:x + BLOCK] = 1.0 - min(var / 20.0, 1.0)

        score = float(np.sum(smoothness > HEATMAP_THRESHOLD)) / smoothness.size

        mask = (smoothness > HEATMAP_THRESHOLD).astype(np.float32)
        alpha = mask[:, :, np.newaxis] * 0.65
        original = np.array(img)
        red = np.zeros_like(original, dtype=float)
        red[:, :, 0] = 255
        overlay = np.clip(original * (1 - alpha) + red * alpha, 0, 255).astype(np.uint8)

        out = io.BytesIO()
        Image.fromarray(overlay).save(out, format="PNG")
        img_b64 = base64.b64encode(out.getvalue()).decode()

        return {
            "score": round(score, 3),
            "label": get_label(score),
            "details": {
                "解説": "赤い箇所が不自然に滑らかな領域（AI画像に特有）",
            },
            "image": f"data:image/png;base64,{img_b64}",
        }
    except Exception as e:
        return error_result(str(e))
