import io
import base64
import numpy as np
import cv2
from PIL import Image
from .base import get_label, error_result

BLOCK_SIZE = 32
HEATMAP_THRESHOLD = 0.3


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img).astype(np.uint8)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY).astype(np.float32)

        h, w = gray.shape
        block_h = h // BLOCK_SIZE
        block_w = w // BLOCK_SIZE

        if block_h < 3 or block_w < 3:
            return {"score": 0, "label": "clean", "image": None, "details": {"判定": "画像が小さすぎます"}}

        sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)
        angle = np.arctan2(sobely, sobelx)

        dominant_angles = np.full((block_h, block_w), np.nan)
        valid_mask = np.zeros((block_h, block_w), dtype=bool)

        for i in range(block_h):
            for j in range(block_w):
                by, bx = i * BLOCK_SIZE, j * BLOCK_SIZE
                block_mag = magnitude[by:by + BLOCK_SIZE, bx:bx + BLOCK_SIZE]
                block_ang = angle[by:by + BLOCK_SIZE, bx:bx + BLOCK_SIZE]
                total_mag = float(np.sum(block_mag))
                if total_mag < 10:
                    continue
                weights = block_mag / total_mag
                sin_m = float(np.sum(np.sin(block_ang) * weights))
                cos_m = float(np.sum(np.cos(block_ang) * weights))
                dominant_angles[i, j] = np.arctan2(sin_m, cos_m)
                valid_mask[i, j] = True

        # 隣接ブロックとの勾配方向の差を計算
        anomaly_map = np.zeros((block_h, block_w), dtype=np.float32)
        for i in range(block_h):
            for j in range(block_w):
                if not valid_mask[i, j]:
                    continue
                diffs = []
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < block_h and 0 <= nj < block_w and valid_mask[ni, nj]:
                        d = dominant_angles[i, j] - dominant_angles[ni, nj]
                        diffs.append(float(np.abs(np.arctan2(np.sin(d), np.cos(d)))))
                if diffs:
                    anomaly_map[i, j] = float(np.mean(diffs)) / np.pi  # 0–1に正規化

        total_valid = float(np.sum(valid_mask))
        score = float(np.sum(anomaly_map > HEATMAP_THRESHOLD)) / total_valid if total_valid > 0 else 0.0

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
            judgment = "背景に不自然な歪みが検出されました"
        elif score >= 0.3:
            judgment = "一部に歪みの疑いがあります"
        else:
            judgment = "不自然な歪みは検出されませんでした"

        return {
            "score": round(score, 3),
            "label": get_label(score),
            "image": f"data:image/png;base64,{img_b64}",
            "details": {
                "判定": judgment,
                "解説": "赤くハイライトされた箇所が隣接ブロック間で勾配方向が急変している（歪みの疑い）領域です",
            },
        }
    except Exception as e:
        return error_result(str(e))
