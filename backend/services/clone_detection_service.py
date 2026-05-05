import io
import base64
import numpy as np
from PIL import Image, ImageDraw
from .base import get_label, error_result

MAX_SIZE = 512
BLOCK_SIZE = 16
STEP = 8
VARIANCE_THRESHOLD = 150
MIN_DISTANCE = 40


def _block_hash(block: np.ndarray):
    if np.var(block) < VARIANCE_THRESHOLD:
        return None
    hh, hw = BLOCK_SIZE // 2, BLOCK_SIZE // 2
    q1 = tuple((np.mean(block[:hh, :hw], axis=(0, 1)).astype(int) // 8 * 8).tolist())
    q2 = tuple((np.mean(block[:hh, hw:], axis=(0, 1)).astype(int) // 8 * 8).tolist())
    q3 = tuple((np.mean(block[hh:, :hw], axis=(0, 1)).astype(int) // 8 * 8).tolist())
    q4 = tuple((np.mean(block[hh:, hw:], axis=(0, 1)).astype(int) // 8 * 8).tolist())
    return q1 + q2 + q3 + q4


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        if max(img.size) > MAX_SIZE:
            img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)

        arr = np.array(img)
        h, w = arr.shape[:2]
        blocks: dict = {}

        for y in range(0, h - BLOCK_SIZE, STEP):
            for x in range(0, w - BLOCK_SIZE, STEP):
                key = _block_hash(arr[y:y + BLOCK_SIZE, x:x + BLOCK_SIZE])
                if key is None:
                    continue
                blocks.setdefault(key, []).append((y, x))

        clone_pairs = []
        for positions in blocks.values():
            if len(positions) < 2:
                continue
            for i in range(len(positions)):
                for j in range(i + 1, min(i + 4, len(positions))):
                    y1, x1 = positions[i]
                    y2, x2 = positions[j]
                    if np.hypot(y1 - y2, x1 - x2) > MIN_DISTANCE:
                        clone_pairs.append(((y1, x1), (y2, x2)))

        vis = img.copy()
        draw = ImageDraw.Draw(vis)
        for (y1, x1), (y2, x2) in clone_pairs[:30]:
            draw.rectangle([x1, y1, x1 + BLOCK_SIZE, y1 + BLOCK_SIZE], outline="red", width=2)
            draw.rectangle([x2, y2, x2 + BLOCK_SIZE, y2 + BLOCK_SIZE], outline="blue", width=2)

        out = io.BytesIO()
        vis.save(out, format="PNG")
        vis_b64 = base64.b64encode(out.getvalue()).decode()

        score = min(len(clone_pairs) / 40.0, 1.0)
        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "clone_pairs_found": len(clone_pairs),
                "note": "赤と青のボックスはコピー&ペーストの可能性がある領域を示します",
            },
            "image": f"data:image/png;base64,{vis_b64}",
        }
    except Exception as e:
        return error_result(str(e))
