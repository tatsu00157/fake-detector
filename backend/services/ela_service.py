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
        score = min(std / 20.0, 1.0)

        out = io.BytesIO()
        Image.fromarray(amplified).save(out, format="PNG")
        ela_b64 = base64.b64encode(out.getvalue()).decode()

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "mean_error": round(mean, 3),
                "std_error": round(std, 3),
                "is_jpeg": is_jpeg,
                "note": "誤差レベルの分散が高い領域は編集の可能性があります",
            },
            "image": f"data:image/png;base64,{ela_b64}",
        }
    except Exception as e:
        return error_result(str(e))
