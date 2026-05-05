from fastapi import APIRouter, UploadFile, File, HTTPException
from services import exif_service, ela_service, fft_service, pixel_stats_service, clone_detection_service, face_service

router = APIRouter(tags=["analysis"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = 20 * 1024 * 1024
SCORE_KEYS = ["exif", "ela", "fft", "pixel_stats", "clone_detection"]


def _validate(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"非対応のファイル形式です: {file.content_type}")


def _overall(results: dict) -> tuple:
    score = sum(results[k]["score"] for k in SCORE_KEYS) / len(SCORE_KEYS)
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
    }
    overall_score, overall_label = _overall(results)
    return {**results, "overall_score": overall_score, "overall_label": overall_label}
