from PIL import Image
import io

_pipe = None


def _get_pipe():
    global _pipe
    if _pipe is None:
        from transformers import pipeline
        _pipe = pipeline("image-classification", model="umm-maybe/AI-image-detector")
    return _pipe


def analyze(image_bytes: bytes) -> dict:
    try:
        pipe = _get_pipe()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = pipe(image)

        ai_score = next((r["score"] for r in results if r["label"] == "artificial"), 0.0)
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
