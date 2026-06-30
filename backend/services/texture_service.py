import io
import base64
import numpy as np
from PIL import Image
from .base import get_label, error_result


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img, dtype=float)
        gray = np.mean(arr, axis=2)

        block = 8
        h, w = gray.shape
        smoothness = np.zeros((h, w), dtype=float)

        block_vars = []
        for y in range(0, h - block, block):
            for x in range(0, w - block, block):
                patch = gray[y:y + block, x:x + block]
                var = float(np.var(patch))
                block_vars.append(var)
                smoothness[y:y + block, x:x + block] = 1.0 - min(var / 80.0, 1.0)

        # 赤オーバーレイ（滑らかな箇所ほど赤く）
        original = np.array(img)
        red = np.zeros_like(original)
        red[:, :, 0] = 255
        alpha = smoothness[:, :, np.newaxis] * 0.65
        overlay = np.clip(original * (1 - alpha) + red * alpha, 0, 255).astype(np.uint8)

        block_vars_arr = np.array(block_vars)
        mean_smoothness = float(np.mean(smoothness))
        # 分散800超のブロック割合：カメラ写真は髪・草・布など必ず存在、AI画像はほぼない
        fine_detail_fraction = float(np.mean(block_vars_arr > 800))
        score = max(0.0, min(mean_smoothness * (1.0 - fine_detail_fraction * 5.0) / 0.5, 1.0))

        out = io.BytesIO()
        Image.fromarray(overlay).save(out, format="PNG")
        img_b64 = base64.b64encode(out.getvalue()).decode()

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "解説": "赤い箇所が不自然に滑らかな領域（AI画像に特有）",
            },
            "image": f"data:image/png;base64,{img_b64}",
        }
    except Exception as e:
        return error_result(str(e))
