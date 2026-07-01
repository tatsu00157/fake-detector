import io
import base64
import numpy as np
import cv2
from PIL import Image
from .base import get_label, error_result

BLOCK_SIZE = 16


def _skin_mask(arr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    mask1 = cv2.inRange(hsv, np.array([0, 30, 60]), np.array([20, 150, 255]))
    mask2 = cv2.inRange(hsv, np.array([170, 30, 60]), np.array([180, 150, 255]))
    return cv2.bitwise_or(mask1, mask2)


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

        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        hf_map = np.abs(laplacian)

        skin = _skin_mask(arr)
        region_mask = cv2.dilate(skin, np.ones((15, 15), np.uint8)) if np.sum(skin) >= 1000 else np.ones((h, w), dtype=np.uint8) * 255

        hf_values = []
        coords = []

        for i in range(block_h):
            for j in range(block_w):
                by, bx = i * BLOCK_SIZE, j * BLOCK_SIZE
                if np.mean(region_mask[by:by + BLOCK_SIZE, bx:bx + BLOCK_SIZE]) < 128:
                    continue
                hf_values.append(float(np.mean(hf_map[by:by + BLOCK_SIZE, bx:bx + BLOCK_SIZE])))
                coords.append((i, j))

        if not hf_values:
            return {"score": 0, "label": "clean", "image": None, "details": {"判定": "解析対象領域が見つかりませんでした"}}

        hf_arr = np.array(hf_values)
        mean_hf = np.mean(hf_arr) + 1e-8
        threshold = mean_hf * 0.4

        anomaly_map = np.zeros((block_h, block_w), dtype=np.float32)
        for idx, (i, j) in enumerate(coords):
            if hf_values[idx] < threshold:
                anomaly_map[i, j] = 1 - (hf_values[idx] / mean_hf)

        valid = anomaly_map[anomaly_map > 0]
        score = float(np.mean(valid)) if len(valid) > 0 else 0.0
        score = min(score * 2.0, 1.0)

        mask_small = (anomaly_map > 0.3).astype(np.uint8) * 255
        mask = cv2.resize(mask_small, (w, h), interpolation=cv2.INTER_NEAREST).astype(np.float32) / 255.0
        alpha = mask[:, :, np.newaxis] * 0.6
        red = np.zeros_like(arr, dtype=np.float32)
        red[:, :, 0] = 200
        overlay = np.clip(arr.astype(np.float32) * (1 - alpha) + red * alpha, 0, 255).astype(np.uint8)

        out = io.BytesIO()
        Image.fromarray(overlay).save(out, format="PNG")
        img_b64 = base64.b64encode(out.getvalue()).decode()

        if score >= 0.6:
            judgment = "不自然な平滑化処理が検出されました"
        elif score >= 0.3:
            judgment = "一部にテクスチャの均一化が見られます"
        else:
            judgment = "不自然な平滑化は検出されませんでした"

        return {
            "score": round(score, 3),
            "label": get_label(score),
            "image": f"data:image/png;base64,{img_b64}",
            "details": {
                "判定": judgment,
                "解説": "赤くハイライトされた箇所が本来あるべき質感が失われている領域を示しています",
            },
        }
    except Exception as e:
        return error_result(str(e))
