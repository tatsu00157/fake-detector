from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services import diff_service, similarity_service
from dependencies.auth import check_usage

router = APIRouter(tags=["compare"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = 20 * 1024 * 1024


def _validate(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"非対応のファイル形式です: {file.content_type}")


@router.post("/compare")
async def compare_images(file1: UploadFile = File(...), file2: UploadFile = File(...), _user=Depends(check_usage)):
    _validate(file1)
    _validate(file2)

    bytes1 = await file1.read()
    bytes2 = await file2.read()

    if len(bytes1) > MAX_BYTES or len(bytes2) > MAX_BYTES:
        raise HTTPException(400, "ファイルサイズが大きすぎます（最大20MB）")

    return {
        "diff":       diff_service.analyze(bytes1, bytes2),
        "similarity": similarity_service.analyze(bytes1, bytes2),
    }
