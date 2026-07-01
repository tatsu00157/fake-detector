import io
import base64
import numpy as np
import cv2
from PIL import Image
from .base import get_label, error_result

BLOCK_SIZE = 16
ELA_THRESHOLD = 10  # 絶対値閾値（0-255スケール）


def analyze(image_bytes: bytes) -> dict:
    try:
        img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img_pil).astype(np.uint8)
        h, w = arr.shape[:2]

        block_h = h // BLOCK_SIZE
        block_w = w // BLOCK_SIZE

        if block_h < 2 or block_w < 2:
            return {"score": 0, "label": "clean", "image": None, "details": {"判定": "画像が小さすぎます"}}

        buf = io.BytesIO()
        img_pil.save(buf, format="JPEG", quality=75)
        buf.seek(0)
        recompressed = np.array(Image.open(buf).convert("RGB")).astype(np.float32)
        ela_gray = np.mean(np.abs(arr.astype(np.float32) - recompressed), axis=2)

        ela_block = np.zeros((block_h, block_w))
        for i in range(block_h):
            for j in range(block_w):
                by, bx = i * BLOCK_SIZE, j * BLOCK_SIZE
                ela_block[i, j] = float(np.mean(ela_gray[by:by + BLOCK_SIZE, bx:bx + BLOCK_SIZE]))

        score = float(np.sum(ela_block > ELA_THRESHOLD)) / ela_block.size

        mask_small = (ela_block > ELA_THRESHOLD).astype(np.uint8) * 255
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
                "解説": "赤くハイライトされた箇所がJPEG再圧縮誤差の高い（切り貼り・合成の疑いがある）領域です",
            },
        }
    except Exception as e:
        return error_result(str(e))
