import numpy as np
import cv2
from PIL import Image
import io
import base64

BLOCK_SIZE = 64


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img).astype(np.uint8)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY).astype(np.float32)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = gray - blurred

        h, w = noise.shape
        block_h = h // BLOCK_SIZE
        block_w = w // BLOCK_SIZE

        if block_h < 2 or block_w < 2:
            return {"score": 0, "label": "clean", "image": None, "details": {"判定": "画像が小さすぎます"}}

        block_stds = np.zeros((block_h, block_w))
        for i in range(block_h):
            for j in range(block_w):
                block = noise[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE, j*BLOCK_SIZE:(j+1)*BLOCK_SIZE]
                block_stds[i, j] = np.std(block)

        mean_std = np.mean(block_stds)
        if mean_std == 0:
            return {"score": 0, "label": "clean", "image": None, "details": {"判定": "解析不能"}}

        deviation = np.abs(block_stds - mean_std) / mean_std
        inconsistent_ratio = float(np.mean(deviation > 0.5))

        mask_small = (deviation > 0.5).astype(np.uint8) * 255
        mask = cv2.resize(mask_small, (w, h), interpolation=cv2.INTER_NEAREST)
        original_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        overlay = original_bgr.copy()
        overlay[mask > 0] = overlay[mask > 0] * 0.4 + np.array([0, 0, 200]) * 0.6

        _, buf = cv2.imencode(".jpg", overlay)
        img_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf).decode()}"

        score = min(inconsistent_ratio * 2.0, 1.0)
        label = "suspicious" if score > 0.6 else "warning" if score > 0.3 else "clean"

        return {
            "score": round(score, 3),
            "label": label,
            "image": img_b64,
            "details": {
                "不整合領域の割合": f"{round(inconsistent_ratio * 100, 1)}%",
                "判定": "ノイズパターンに不整合あり（合成の疑い）" if score > 0.6 else "やや不整合あり" if score > 0.3 else "ノイズパターンは整合",
                "見方": "赤くハイライトされた箇所がノイズパターンの不整合を示しています",
            },
        }
    except Exception as e:
        return {"score": 0, "label": "error", "image": None, "details": {"エラー": str(e)}}
