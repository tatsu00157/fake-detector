import io
import base64
import numpy as np
import cv2
from PIL import Image
from .base import get_label, error_result

BLOCK_SIZE = 16


def analyze(image_bytes: bytes) -> dict:
    try:
        img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img_pil).astype(np.uint8)
        h, w = arr.shape[:2]

        block_h = h // BLOCK_SIZE
        block_w = w // BLOCK_SIZE

        if block_h < 2 or block_w < 2:
            return {"score": 0, "label": "clean", "image": None, "details": {"判定": "画像が小さすぎます"}}

        # ELA: re-compress at quality 75 and compute difference
        buf = io.BytesIO()
        img_pil.save(buf, format="JPEG", quality=75)
        buf.seek(0)
        recompressed = np.array(Image.open(buf).convert("RGB")).astype(np.float32)
        ela = np.abs(arr.astype(np.float32) - recompressed)
        ela_gray = np.mean(ela, axis=2)

        # Edge proximity: high ELA near edges = suspicious boundary
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_region = cv2.dilate(edges, np.ones((5, 5), np.uint8))

        ela_block = np.zeros((block_h, block_w))
        for i in range(block_h):
            for j in range(block_w):
                by, bx = i * BLOCK_SIZE, j * BLOCK_SIZE
                block_ela = ela_gray[by:by + BLOCK_SIZE, bx:bx + BLOCK_SIZE]
                block_edge = edge_region[by:by + BLOCK_SIZE, bx:bx + BLOCK_SIZE]
                edge_weight = float(np.mean(block_edge)) / 255.0 + 0.1
                ela_block[i, j] = float(np.mean(block_ela)) * edge_weight

        mean_ela = np.mean(ela_block)
        std_ela = np.std(ela_block) + 1e-8
        z_scores = (ela_block - mean_ela) / std_ela
        anomaly_map = np.clip(z_scores / 3.0, 0, 1)

        score = float(np.mean(anomaly_map))
        score = min(score * 4.0, 1.0)

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
            judgment = "切り貼り・合成の痕跡が強く検出されました"
        elif score >= 0.3:
            judgment = "一部に合成の痕跡の疑いがあります"
        else:
            judgment = "切り貼り・合成の痕跡は検出されませんでした"

        return {
            "score": round(score, 3),
            "label": get_label(score),
            "image": f"data:image/png;base64,{img_b64}",
            "details": {
                "判定": judgment,
                "解説": "赤くハイライトされた箇所がJPEG圧縮誤差とエッジの不自然さから合成・切り貼りの疑いがある領域です",
            },
        }
    except Exception as e:
        return error_result(str(e))
