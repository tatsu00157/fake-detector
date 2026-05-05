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

CAMERA_FIELD_LABELS = {
    "Image Make":           "カメラメーカー",
    "Image Model":          "カメラ機種",
    "EXIF DateTimeOriginal":"撮影日時",
    "EXIF ExposureTime":    "シャッタースピード",
    "EXIF ISOSpeedRatings": "ISO感度",
    "EXIF FNumber":         "絞り値（F値）",
    "EXIF FocalLength":     "焦点距離",
    "GPS GPSLatitude":      "GPS緯度",
    "GPS GPSLongitude":     "GPS経度",
    "Image Software":       "ソフトウェア",
    "EXIF Flash":           "フラッシュ",
    "EXIF WhiteBalance":    "ホワイトバランス",
}


def analyze(image_bytes: bytes) -> dict:
    try:
        tags = exifread.process_file(io.BytesIO(image_bytes), details=False)

        if not tags:
            return {
                "score": 0.2,
                "label": "warning",
                "details": {
                    "カメラ情報": "なし（AI生成画像はカメラ情報を持たないことが多い）",
                },
                "image": None,
            }

        raw_tags = {str(k): str(v) for k, v in tags.items()}
        all_values = " ".join(raw_tags.values()).lower()
        software = raw_tags.get("Image Software", "").lower()

        ai_signatures = [t for t in AI_TOOL_SIGNATURES if t in all_values]

        # 全フィールドを値あり・なし問わず表示
        metadata = {}
        for field, label in CAMERA_FIELD_LABELS.items():
            metadata[label] = raw_tags[field] if field in raw_tags else "なし"

        core_fields = ["Image Make", "Image Model", "EXIF ExposureTime", "EXIF ISOSpeedRatings", "EXIF FocalLength"]
        missing_count = sum(1 for f in core_fields if f not in raw_tags)

        score = 0.0
        if ai_signatures:
            score = 0.95
            metadata["AI署名"] = "、".join(ai_signatures)
        elif any(t in software for t in AI_TOOL_SIGNATURES):
            score = 0.85
            metadata["AI署名"] = raw_tags.get("Image Software", "")
        elif missing_count >= 4:
            score = 0.4

        return {
            "score": float(score),
            "label": get_label(score),
            "details": metadata,
            "image": None,
        }
    except Exception as e:
        return error_result(str(e))
