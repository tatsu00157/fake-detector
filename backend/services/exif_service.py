import io
import exifread
from .base import get_label, error_result

AI_TOOL_SIGNATURES = [
    "stable diffusion", "midjourney", "dall-e", "dall·e",
    "adobe firefly", "imagen", "dreamstudio", "novelai",
    "automatic1111", "comfyui", "invokeai", "fooocus",
    "getimg", "nightcafe", "dreamlike", "lexica",
    "ai generated", "ai-generated", "generative",
]

EXPECTED_CAMERA_FIELDS = [
    "EXIF ExposureTime",
    "EXIF ISOSpeedRatings",
    "EXIF FocalLength",
    "Image Make",
    "Image Model",
]


def analyze(image_bytes: bytes) -> dict:
    try:
        tags = exifread.process_file(io.BytesIO(image_bytes), details=False)

        if not tags:
            return {
                "score": 0.2,
                "label": "warning",
                "details": {
                    "message": "EXIFデータが見つかりません（AI生成画像はEXIFを持たないことが多い）",
                    "ai_signatures": [],
                    "raw_tags": {},
                },
                "image": None,
            }

        raw_tags = {str(k): str(v) for k, v in tags.items()}
        all_values = " ".join(raw_tags.values()).lower()

        ai_signatures = [t for t in AI_TOOL_SIGNATURES if t in all_values]
        missing_fields = [f for f in EXPECTED_CAMERA_FIELDS if f not in raw_tags]
        software = raw_tags.get("Image Software", "").lower()

        score = 0.0
        if ai_signatures:
            score = 0.95
        elif any(t in software for t in AI_TOOL_SIGNATURES):
            score = 0.85
        elif len(missing_fields) >= 4:
            score = 0.4

        camera = f"{raw_tags.get('Image Make', '')} {raw_tags.get('Image Model', '')}".strip()

        return {
            "score": float(score),
            "label": get_label(score),
            "details": {
                "ai_signatures": ai_signatures,
                "missing_camera_fields": missing_fields,
                "software": raw_tags.get("Image Software", "（なし）"),
                "camera": camera or "（なし）",
                "datetime": raw_tags.get("EXIF DateTimeOriginal", "（なし）"),
            },
            "image": None,
        }
    except Exception as e:
        return error_result(str(e))
