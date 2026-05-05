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

        global_score = min(std / 12.0, 1.0)
        hotspot_score = min(local_max_std / 15.0, 1.0)
        score = max(global_score, hotspot_score)

        # PNGはJPEG変換時に均一なアーティファクトが発生するためスコアを補正
        if not is_jpeg:
            score = score * 0.6

        out = io.BytesIO()
        Image.fromarray(amplified).save(out, format="PNG")
        ela_b64 = base64.b64encode(out.getvalue()).decode()

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "mean_error": round(mean, 3),
                "std_error": round(std, 3),
                "hotspot_std": round(local_max_std, 3),
                "is_jpeg": is_jpeg,
                "note": "誤差レベルの分散・局所的なホットスポットが高い場合は編集の可能性があります",
            },
            "image": f"data:image/png;base64,{ela_b64}",
        }
    except Exception as e:
        return error_result(str(e))
