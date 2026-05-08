import io
import base64
import cv2
import numpy as np
from PIL import Image
from .base import get_label, error_result


def analyze(image_bytes: bytes) -> dict:
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        if img_cv is None:
            return error_result("画像デコードに失敗しました")

        h, w = img_cv.shape[:2]
        if max(h, w) > 1024:
            scale = 1024 / max(h, w)
            img_cv = cv2.resize(img_cv, (int(w * scale), int(h * scale)))
            img_pil = img_pil.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        b_ch, g_ch, r_ch = [img_cv[:, :, i].astype(np.float32) for i in range(3)]

        def gradient_mag(ch):
            gx = cv2.Sobel(ch, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(ch, cv2.CV_32F, 0, 1, ksize=3)
            return np.sqrt(gx ** 2 + gy ** 2)

        mag_r = gradient_mag(r_ch)
        mag_g = gradient_mag(g_ch)
        mag_b = gradient_mag(b_ch)
        mag_combined = (mag_r + mag_g + mag_b) / 3

        # 上位20%の強エッジのみ対象
        threshold = np.percentile(mag_combined, 80)
        strong_edges = mag_combined > threshold

        if np.sum(strong_edges) < 200:
            return {
                "score": 0.0,
                "label": "clean",
                "details": {"note": "エッジが少なく解析できませんでした"},
                "image": None,
            }

        # RとBチャンネルの勾配差（色収差の指標）
        # 本物のカメラ: レンズの物理特性でR-Bにズレが生じる
        # AI画像: 物理レンズがないためズレがほぼゼロ
        rb_diff = np.abs(mag_r - mag_b)
        mean_ca = float(np.mean(rb_diff[strong_edges]))
        mean_edge = float(np.mean(mag_combined[strong_edges]))
        ca_ratio = mean_ca / (mean_edge + 1e-8)

        # ca_ratio低い = 色収差なし = AI疑い
        # 0.15以上: 本物らしい / 0.05未満: AIの可能性高い
        ai_score = float(np.clip(1.0 - (ca_ratio / 0.15), 0.0, 1.0))

        # 色収差が少ない強エッジ（下位25%）を赤でハイライト
        low_ca_threshold = float(np.percentile(rb_diff[strong_edges], 25))
        suspicious_mask = strong_edges & (rb_diff < low_ca_threshold)

        overlay = np.zeros((*img_cv.shape[:2], 4), dtype=np.uint8)
        overlay[suspicious_mask] = [255, 0, 0, 150]
        combined = Image.alpha_composite(
            img_pil.convert("RGBA"),
            Image.fromarray(overlay, "RGBA")
        )

        out = io.BytesIO()
        combined.convert("RGB").save(out, format="PNG")
        img_b64 = base64.b64encode(out.getvalue()).decode()

        return {
            "score": float(ai_score),
            "label": get_label(ai_score),
            "details": {
                "色収差比率": round(ca_ratio, 4),
                "AI疑いスコア": round(ai_score, 3),
                "解説": "カメラレンズ由来の色収差（RGB色ズレ）が少ない境界を赤でハイライト。AI生成画像では色収差がほぼ存在しません。",
            },
            "image": f"data:image/png;base64,{img_b64}",
        }
    except Exception as e:
        return error_result(str(e))
