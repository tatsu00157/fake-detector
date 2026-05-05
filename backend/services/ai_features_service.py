import io
import cv2
import numpy as np
from PIL import Image
from .base import get_label, error_result


def _edge_sharpness(gray: np.ndarray) -> tuple:
    """エッジと非エッジ領域の勾配比を計算。AIアニメはエッジが鋭くフラット面との差が大きい。"""
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.sum(edges > 0)) / edges.size

    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_mag = np.sqrt(sobelx ** 2 + sobely ** 2)

    edge_mask = edges > 0
    non_edge_mask = ~edge_mask

    if np.sum(edge_mask) > 100 and np.sum(non_edge_mask) > 100:
        edge_mean     = float(np.mean(sobel_mag[edge_mask]))
        non_edge_mean = float(np.mean(sobel_mag[non_edge_mask]))
        ratio = edge_mean / (non_edge_mean + 1e-8)
    else:
        ratio = 1.0

    return edge_density, ratio


def _color_variety(img_pil: Image.Image) -> float:
    """色の多様性。AIアニメはフラット塗りで色数が少ない。"""
    small = img_pil.resize((128, 128), Image.LANCZOS)
    # JPEGでブラーをかけて圧縮ノイズによる偽色を除去
    buf = io.BytesIO()
    small.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    small_j = Image.open(buf).convert("RGB")
    quantized = small_j.quantize(colors=64)
    color_count = len(set(quantized.getdata()))
    return color_count / 64.0


def analyze(image_bytes: bytes) -> dict:
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        if img_cv is None:
            return error_result("画像デコードに失敗しました")

        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        edge_density, sharpness_ratio = _edge_sharpness(gray)
        color_variety = _color_variety(img_pil)

        # AIアニメ: エッジと非エッジの差が大きい・色数が少ない
        edge_suspicious  = sharpness_ratio > 3.0
        color_suspicious = color_variety < 0.65

        signal_count = (1 if edge_suspicious else 0) + (1 if color_suspicious else 0)
        score = min(signal_count / 2.0 * 0.85, 0.85)

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "エッジ鋭さ比率": round(sharpness_ratio, 3),
                "エッジ密度": round(edge_density, 4),
                "色の多様度": round(color_variety, 3),
                "解説": "エッジが鋭く色数が少ない場合はAI生成（特にアニメ調）の可能性があります",
            },
            "image": None,
        }
    except Exception as e:
        return error_result(str(e))
