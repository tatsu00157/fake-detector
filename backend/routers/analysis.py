from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from core.limiter import limiter
from services import (
    exif_service, ela_service, texture_service, noise_service,
    background_distortion_service, texture_uniformity_service,
    lighting_inconsistency_service, composite_boundary_service,
)

router = APIRouter(tags=["analysis"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = 20 * 1024 * 1024

AI_KEYS           = ["exif", "texture", "noise"]
MANIPULATION_KEYS = ["background_distortion", "texture_uniformity", "lighting_inconsistency", "composite_boundary"]


def _validate(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"非対応のファイル形式です: {file.content_type}")


def _score_label(results: dict, keys: list) -> tuple:
    score = sum(results[k]["score"] for k in keys) / len(keys)
    label = "clean" if score < 0.3 else "warning" if score < 0.6 else "suspicious"
    return round(score, 3), label


@router.post("/analyze")
@limiter.limit("10/minute")
async def analyze_image(request: Request, file: UploadFile = File(...)):
    _validate(file)
    image_bytes = await file.read()
    if len(image_bytes) > MAX_BYTES:
        raise HTTPException(400, "ファイルサイズが大きすぎます（最大20MB）")

    results = {
        "exif":                    exif_service.analyze(image_bytes),
        "ela":                     ela_service.analyze(image_bytes),
        "texture":                 texture_service.analyze(image_bytes),
        "noise":                   noise_service.analyze(image_bytes),
        "background_distortion":   background_distortion_service.analyze(image_bytes),
        "texture_uniformity":      texture_uniformity_service.analyze(image_bytes),
        "lighting_inconsistency":  lighting_inconsistency_service.analyze(image_bytes),
        "composite_boundary":      composite_boundary_service.analyze(image_bytes),
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
