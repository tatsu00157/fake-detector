from fastapi import APIRouter, UploadFile, File, HTTPException
from services import (
    exif_service, ela_service, fft_service,
    pixel_stats_service, clone_detection_service,
    face_service, ai_features_service,
)

router = APIRouter(tags=["analysis"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = 20 * 1024 * 1024

AI_KEYS           = ["exif", "fft", "pixel_stats", "ai_features"]
MANIPULATION_KEYS = ["ela", "clone_detection"]


def _validate(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"非対応のファイル形式です: {file.content_type}")


def _score_label(results: dict, keys: list) -> tuple:
    score = sum(results[k]["score"] for k in keys) / len(keys)
    label = "clean" if score < 0.3 else "warning" if score < 0.6 else "suspicious"
    return round(score, 3), label


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    _validate(file)
    image_bytes = await file.read()
    if len(image_bytes) > MAX_BYTES:
        raise HTTPException(400, "ファイルサイズが大きすぎます（最大20MB）")

    results = {
        "exif":            exif_service.analyze(image_bytes),
        "ela":             ela_service.analyze(image_bytes),
        "fft":             fft_service.analyze(image_bytes),
        "pixel_stats":     pixel_stats_service.analyze(image_bytes),
        "clone_detection": clone_detection_service.analyze(image_bytes),
        "face_detection":  face_service.analyze(image_bytes),
        "ai_features":     ai_features_service.analyze(image_bytes),
    }

    ai_score,           ai_label           = _score_label(results, AI_KEYS)
    manipulation_score, manipulation_label = _score_label(results, MANIPULATION_KEYS)

    return {
        **results,
        "ai_score":           ai_score,
        "ai_label":           ai_label,
        "manipulation_score": manipulation_score,
        "manipulation_label": manipulation_label,
    }
