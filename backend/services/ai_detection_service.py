from PIL import Image
import io

_pipe = None

_AI_LABELS = {"ai", "artificial", "generated", "fake", "ai-generated", "label_1"}
_REAL_LABELS = {"not-ai", "real", "not_ai", "notai", "label_0", "human"}


def _get_pipe():
    global _pipe
    if _pipe is None:
        from transformers import pipeline
        _pipe = pipeline("image-classification", model="dima806/ai_vs_real_image_detection")
    return _pipe


def _find_ai_score(results: list) -> float:
    print(f"[ai_detection] raw results: {results}")
    for r in results:
        normalized = r["label"].lower().replace(" ", "-").replace("_", "-")
        if normalized in _REAL_LABELS:
            return 1.0 - r["score"]
        if normalized in _AI_LABELS:
            return r["score"]
    return results[0]["score"] if results else 0.0


def analyze(image_bytes: bytes) -> dict:
    try:
        pipe = _get_pipe()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=95)
        buf.seek(0)
        image = Image.open(buf).convert("RGB")
        results = pipe(image)

        ai_score = _find_ai_score(results)
        label = "suspicious" if ai_score > 0.7 else "warning" if ai_score > 0.4 else "clean"

        return {
            "score": round(ai_score, 3),
            "label": label,
            "image": None,
            "details": {
                "AI生成の可能性": f"{round(ai_score * 100, 1)}%",
                "判定": "AI生成の疑いが強い" if ai_score > 0.7 else "判断困難" if ai_score > 0.4 else "本物の可能性が高い",
            },
        }
    except Exception as e:
        return {"score": 0, "label": "error", "image": None, "details": {"エラー": str(e)}}
