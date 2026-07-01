import io
import base64
import numpy as np
from PIL import Image, ImageChops
from .base import get_label, error_result


def analyze(image_bytes: bytes) -> dict:
    try:
        original = Image.open(io.BytesIO(image_bytes))
        is_jpeg = original.format == "JPEG"
        original_rgb = original.convert("RGB")

        buffer = io.BytesIO()
        original_rgb.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)
        recompressed = Image.open(buffer).convert("RGB")

        diff = ImageChops.difference(original_rgb, recompressed)
        diff_arr = np.array(diff).astype(float)
        amplified = np.clip(diff_arr * 20, 0, 255).astype(np.uint8)

        mean = float(np.mean(diff_arr))
        std = float(np.std(diff_arr))

        # 局所ホットスポット検出
        gray_diff = np.mean(diff_arr, axis=2)
        h, w = gray_diff.shape
        block = 16
        local_maxes = [
            np.max(gray_diff[y:y + block, x:x + block])
            for y in range(0, h - block, block)
            for x in range(0, w - block, block)
        ]
        local_max_std = float(np.std(local_maxes)) if local_maxes else 0.0

        score = min(float(np.mean(diff_arr)) / 12.0, 1.0)

        # PNGはJPEG変換時に均一なアーティファクトが発生するためスコアを補正
        if not is_jpeg:
            score = score * 0.6

        out = io.BytesIO()
        Image.fromarray(amplified).save(out, format="PNG")
        ela_b64 = base64.b64encode(out.getvalue()).decode()

        if score >= 0.6:
            judgment = "編集・加工の痕跡が検出されました"
        elif score >= 0.3:
            judgment = "一部に不審な箇所があります"
        else:
            judgment = "編集・加工の痕跡は検出されませんでした"

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "ファイル形式": "JPEG" if is_jpeg else "PNG",
                "判定": judgment,
            },
            "image": f"data:image/png;base64,{ela_b64}",
        }
    except Exception as e:
        return error_result(str(e))
