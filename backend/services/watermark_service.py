import io
import numpy as np
from PIL import Image
from .base import get_label, error_result

SD_WATERMARK = bytes([0x53, 0x74, 0x65, 0x61, 0x6C, 0x74])  # "Stealt" prefix check


def analyze(image_bytes: bytes) -> dict:
    try:
        import cv2
        from imwatermark import WatermarkDecoder

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img)
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

        decoder = WatermarkDecoder("bytes", 48)
        watermark = decoder.decode(bgr, "dwtDct")

        detected = watermark is not None and len(watermark) > 0 and any(b != 0 for b in watermark)

        return {
            "score": 1.0 if detected else 0.0,
            "label": "suspicious" if detected else "clean",
            "details": {
                "detected": detected,
                "note": "Stable Diffusionの不可視透かしが検出されました" if detected else "不可視透かしは検出されませんでした",
            },
            "image": None,
        }

    except ImportError:
        return {
            "score": 0.0,
            "label": "info",
            "details": {"note": "invisible-watermark未インストール"},
            "image": None,
        }
    except Exception as e:
        return error_result(str(e))
