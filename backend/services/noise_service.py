import io
import base64
import numpy as np
import cv2
from PIL import Image
from .base import get_label, error_result


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img, dtype=np.float32)
        gray = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)

        # ガウシアンブラーとの差分でノイズ残差を抽出
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = gray - blurred

        # ブロックごとのノイズ分散を計算（低い = ノイズが少なすぎる = AI特有）
        block = 16
        h, w = gray.shape
        noise_map = np.zeros((h, w), dtype=np.float32)

        noise_vars = []
        for y in range(0, h - block, block):
            for x in range(0, w - block, block):
                patch = noise[y:y + block, x:x + block]
                var = float(np.var(patch))
                noise_vars.append(var)
                noise_map[y:y + block, x:x + block] = 1.0 - min(var / 1.0, 1.0)

        # 赤オーバーレイ（ノイズが少なすぎる箇所ほど赤く）
        original = arr.astype(np.uint8)
        red = np.zeros_like(original)
        red[:, :, 0] = 255
        alpha = noise_map[:, :, np.newaxis] * 0.65
        overlay = np.clip(original * (1 - alpha) + red * alpha, 0, 255).astype(np.uint8)

        noise_vars_arr = np.array(noise_vars)
        mean_noise_var = float(np.mean(noise_vars_arr))
        cv_noise = float(np.std(noise_vars_arr)) / (mean_noise_var + 1e-8)
        # AI画像：均一に低ノイズ（低mean・低CV）→高スコア
        # カメラ写真：ノイズが高いまたは不均一（高CV）→低スコア
        low_noise_component = max(0.0, 1.0 - mean_noise_var / 5.0)
        uniform_component = max(0.0, 1.0 - cv_noise / 2.0)
        score = low_noise_component * uniform_component

        out = io.BytesIO()
        Image.fromarray(overlay).save(out, format="PNG")
        img_b64 = base64.b64encode(out.getvalue()).decode()

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "解説": "赤い箇所がノイズの少なすぎる領域（AI画像に特有）",
            },
            "image": f"data:image/png;base64,{img_b64}",
        }
    except Exception as e:
        return error_result(str(e))
