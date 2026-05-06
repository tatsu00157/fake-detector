import numpy as np
import cv2
from PIL import Image
import io
import base64

BLOCK_SIZE = 8


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY).astype(np.float32)

        h, w = gray.shape
        block_h = h // BLOCK_SIZE
        block_w = w // BLOCK_SIZE

        if block_h < 4 or block_w < 4:
            return {"score": 0, "label": "clean", "image": None, "details": {"判定": "画像が小さすぎます"}}

        ac_energies = np.zeros((block_h, block_w))
        for i in range(block_h):
            for j in range(block_w):
                block = gray[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE, j*BLOCK_SIZE:(j+1)*BLOCK_SIZE] - 128
                d = cv2.dct(block)
                d[0, 0] = 0
                ac_energies[i, j] = np.sum(d ** 2)

        log_e = np.log1p(ac_energies)
        mean_e = np.mean(log_e)
        std_e = np.std(log_e)

        if std_e == 0:
            return {"score": 0, "label": "clean", "image": None, "details": {"判定": "解析不能"}}

        z_scores = np.abs((log_e - mean_e) / std_e)
        suspicious_ratio = float(np.mean(z_scores > 2.0))

        heatmap_small = (np.clip(z_scores / 4.0, 0, 1) * 255).astype(np.uint8)
        heatmap = cv2.resize(heatmap_small, (w, h), interpolation=cv2.INTER_NEAREST)
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_HOT)
        original_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        overlay = cv2.addWeighted(original_bgr, 0.6, heatmap_color, 0.4, 0)

        _, buf = cv2.imencode(".jpg", overlay)
        img_b64 = base64.b64encode(buf).decode()

        score = min(suspicious_ratio * 3.0, 1.0)
        label = "suspicious" if score > 0.6 else "warning" if score > 0.3 else "clean"

        return {
            "score": round(score, 3),
            "label": label,
            "image": img_b64,
            "details": {
                "異常ブロック割合": f"{round(suspicious_ratio * 100, 1)}%",
                "判定": "周波数統計に異常あり（合成の疑い）" if score > 0.6 else "やや異常あり" if score > 0.3 else "周波数統計は正常",
            },
        }
    except Exception as e:
        return {"score": 0, "label": "error", "image": None, "details": {"エラー": str(e)}}
