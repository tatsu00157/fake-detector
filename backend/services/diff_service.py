import io
import base64
import numpy as np
import cv2
from PIL import Image
from .base import error_result


def analyze(image_bytes1: bytes, image_bytes2: bytes) -> dict:
    try:
        img1 = Image.open(io.BytesIO(image_bytes1)).convert("RGB")
        img2 = Image.open(io.BytesIO(image_bytes2)).convert("RGB")

        # 小さい方に合わせてリサイズ
        w = min(img1.width, img2.width)
        h = min(img1.height, img2.height)
        img1 = img1.resize((w, h))
        img2 = img2.resize((w, h))

        arr1 = np.array(img1, dtype=np.float32)
        arr2 = np.array(img2, dtype=np.float32)

        diff = np.abs(arr1 - arr2)
        mean_diff = float(np.mean(diff))
        score = min(mean_diff / 50.0, 1.0)

        # 差分を赤でハイライト
        gray_diff = np.mean(diff, axis=2)
        mask = (gray_diff > 15).astype(np.float32)
        red = np.zeros_like(arr1)
        red[:, :, 0] = 255
        alpha = mask[:, :, np.newaxis] * 0.7
        overlay = np.clip(arr1 * (1 - alpha) + red * alpha, 0, 255).astype(np.uint8)

        out = io.BytesIO()
        Image.fromarray(overlay).save(out, format="PNG")
        img_b64 = base64.b64encode(out.getvalue()).decode()

        if score >= 0.6:
            judgment = "2枚の画像に大きな差異があります"
        elif score >= 0.3:
            judgment = "一部に差異があります"
        else:
            judgment = "ほぼ同一の画像です"

        return {
            "score": float(score),
            "label": "diff",
            "details": {"判定": judgment},
            "image": f"data:image/png;base64,{img_b64}",
        }
    except Exception as e:
        return error_result(str(e))
