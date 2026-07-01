import io
import base64
import numpy as np
import cv2
from PIL import Image
from .base import get_label, error_result

BLOCK = 16
HEATMAP_THRESHOLD = 0.7  # noise_map > 0.7 = noise variance < 1.5 = ノイズが少なすぎる


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img, dtype=np.float32)
        gray = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = gray - blurred

        h, w = gray.shape
        noise_map = np.zeros((h, w), dtype=np.float32)

        for y in range(0, h - BLOCK, BLOCK):
            for x in range(0, w - BLOCK, BLOCK):
                patch = noise[y:y + BLOCK, x:x + BLOCK]
                var = float(np.var(patch))
                noise_map[y:y + BLOCK, x:x + BLOCK] = 1.0 - min(var / 5.0, 1.0)

        score = float(np.sum(noise_map > HEATMAP_THRESHOLD)) / noise_map.size

        mask = (noise_map > HEATMAP_THRESHOLD).astype(np.float32)
        original = arr.astype(np.uint8)
        alpha = mask[:, :, np.newaxis] * 0.65
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
                "解説": "赤い箇所がノイズの少なすぎる領域（AI画像に特有）",
            },
            "image": f"data:image/png;base64,{img_b64}",
        }
    except Exception as e:
        return error_result(str(e))
