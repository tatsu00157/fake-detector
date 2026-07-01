import io
import base64
import numpy as np
import cv2
from PIL import Image
from .base import get_label, error_result

BLOCK_SIZE = 64


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img).astype(np.uint8)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY).astype(np.float32)

        h, w = gray.shape
        block_h = h // BLOCK_SIZE
        block_w = w // BLOCK_SIZE

        if block_h < 2 or block_w < 2:
            return {"score": 0, "label": "clean", "image": None, "details": {"判定": "画像が小さすぎます"}}

        smoothed = cv2.GaussianBlur(gray, (5, 5), 0)
        sobelx = cv2.Sobel(smoothed, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(smoothed, cv2.CV_64F, 0, 1, ksize=5)
        magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)
        angle = np.arctan2(sobely, sobelx)

        dominant_angles = np.full((block_h, block_w), np.nan)

        for i in range(block_h):
            for j in range(block_w):
                by, bx = i * BLOCK_SIZE, j * BLOCK_SIZE
                block_mag = magnitude[by:by + BLOCK_SIZE, bx:bx + BLOCK_SIZE]
                block_ang = angle[by:by + BLOCK_SIZE, bx:bx + BLOCK_SIZE]
                total_mag = np.sum(block_mag)
                if total_mag < 50:
                    continue
                weights = block_mag / total_mag
                sin_mean = np.sum(np.sin(block_ang) * weights)
                cos_mean = np.sum(np.cos(block_ang) * weights)
                dominant_angles[i, j] = np.arctan2(sin_mean, cos_mean)

        valid = dominant_angles[~np.isnan(dominant_angles)]
        if len(valid) < 4:
            return {"score": 0, "label": "clean", "image": None, "details": {"判定": "解析対象が不足しています"}}

        global_angle = np.arctan2(np.mean(np.sin(valid)), np.mean(np.cos(valid)))

        anomaly_map = np.zeros((block_h, block_w))
        for i in range(block_h):
            for j in range(block_w):
                if np.isnan(dominant_angles[i, j]):
                    continue
                diff = dominant_angles[i, j] - global_angle
                circular_diff = np.abs(np.arctan2(np.sin(diff), np.cos(diff)))
                anomaly_map[i, j] = circular_diff / np.pi  # normalize 0–1

        HEATMAP_THRESHOLD = 0.5
        total_valid = float(np.sum(~np.isnan(dominant_angles)))
        score = float(np.sum(anomaly_map > HEATMAP_THRESHOLD)) / total_valid if total_valid > 0 else 0.0
        score = min(score * 3.0, 1.0)

        mask_small = (anomaly_map > HEATMAP_THRESHOLD).astype(np.uint8) * 255
        mask = cv2.resize(mask_small, (w, h), interpolation=cv2.INTER_NEAREST).astype(np.float32) / 255.0
        alpha = mask[:, :, np.newaxis] * 0.6
        red = np.zeros_like(arr, dtype=np.float32)
        red[:, :, 0] = 200
        overlay = np.clip(arr.astype(np.float32) * (1 - alpha) + red * alpha, 0, 255).astype(np.uint8)

        out = io.BytesIO()
        Image.fromarray(overlay).save(out, format="PNG")
        img_b64 = base64.b64encode(out.getvalue()).decode()

        if score >= 0.6:
            judgment = "光源・影の方向に大きな不整合が検出されました"
        elif score >= 0.3:
            judgment = "一部に光源方向の矛盾が見られます"
        else:
            judgment = "光源・影の方向に不整合は検出されませんでした"

        return {
            "score": round(score, 3),
            "label": get_label(score),
            "image": f"data:image/png;base64,{img_b64}",
            "details": {
                "判定": judgment,
                "解説": "赤くハイライトされた箇所が画像内の支配的な光源方向と矛盾している領域です",
            },
        }
    except Exception as e:
        return error_result(str(e))
