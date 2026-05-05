import io
import base64
import numpy as np
from PIL import Image
from .base import get_label, error_result

MAX_SIZE = 512


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        if max(img.size) > MAX_SIZE:
            img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)

        arr = np.array(img, dtype=float)
        h, w = arr.shape

        fft_shift = np.fft.fftshift(np.fft.fft2(arr))
        magnitude = np.log(np.abs(fft_shift) + 1)
        mag_norm = (magnitude - magnitude.min()) / (magnitude.max() - magnitude.min() + 1e-8)

        cy, cx = h // 2, w // 2
        mask_r = min(h, w) // 10
        Y, X = np.ogrid[:h, :w]
        center_mask = (X - cx) ** 2 + (Y - cy) ** 2 < mask_r ** 2

        outer = mag_norm.copy()
        outer[center_mask] = 0

        # しきい値を0.85→0.75に緩めて感度を上げる
        peak_pixels = int(np.sum(outer > 0.75))
        total_outer = int(np.sum(~center_mask))
        peak_ratio = peak_pixels / total_outer if total_outer > 0 else 0.0

        # スコア倍率を60→80に上げる
        score = min(peak_ratio * 80, 1.0)

        out = io.BytesIO()
        Image.fromarray((mag_norm * 255).astype(np.uint8)).save(out, format="PNG")
        fft_b64 = base64.b64encode(out.getvalue()).decode()

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "周期パターン比率": round(float(peak_ratio), 5),
                "周期パターン画素数": peak_pixels,
                "解説": "高周波の規則的なパターンはGAN生成の痕跡を示す可能性があります",
            },
            "image": f"data:image/png;base64,{fft_b64}",
        }
    except Exception as e:
        return error_result(str(e))
