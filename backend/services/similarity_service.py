import io
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import imagehash
from .base import error_result


def analyze(image_bytes1: bytes, image_bytes2: bytes) -> dict:
    try:
        img1 = Image.open(io.BytesIO(image_bytes1)).convert("RGB")
        img2 = Image.open(io.BytesIO(image_bytes2)).convert("RGB")

        # SSIMのために同サイズにリサイズ
        w = min(img1.width, img2.width)
        h = min(img1.height, img2.height)
        img1r = img1.resize((w, h))
        img2r = img2.resize((w, h))

        arr1 = np.array(img1r.convert("L"))
        arr2 = np.array(img2r.convert("L"))
        ssim_score = float(ssim(arr1, arr2, data_range=255))

        # パーセプチュアルハッシュ
        hash1 = imagehash.phash(img1)
        hash2 = imagehash.phash(img2)
        hash_diff = hash1 - hash2
        hash_score = max(0.0, 1.0 - hash_diff / 64.0)

        similarity = round((ssim_score + hash_score) / 2 * 100, 1)

        if similarity >= 90:
            judgment = "ほぼ同一の画像です"
        elif similarity >= 60:
            judgment = "部分的に似ています"
        else:
            judgment = "異なる画像です"

        return {
            "score": similarity / 100.0,
            "label": "similarity",
            "details": {
                "類似度": f"{similarity}%",
                "判定": judgment,
            },
            "image": None,
        }
    except Exception as e:
        return error_result(str(e))
