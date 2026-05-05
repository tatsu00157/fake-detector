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
    "Image Make":                "カメラメーカー",
    "Image Model":               "カメラ機種",
    "EXIF DateTimeOriginal":     "撮影日時",
    "Image DateTime":            "更新日時",
    "EXIF ExposureTime":         "露光時間",
    "EXIF ISOSpeedRatings":      "光の感度（ISO）",
    "EXIF FNumber":              "レンズの明るさ（F値）",
    "EXIF FocalLength":          "焦点距離",
    "EXIF Flash":                "フラッシュ",
    "EXIF WhiteBalance":         "色合いの補正",
    "EXIF SceneCaptureType":     "撮影シーン",
    "EXIF Sharpness":            "シャープネス",
    "EXIF Saturation":           "彩度",
    "EXIF Contrast":             "コントラスト",
    "EXIF LensMake":             "レンズメーカー",
    "EXIF LensModel":            "レンズ機種",
    "EXIF ColorSpace":           "色空間",
    "EXIF ExifImageWidth":       "画像の幅（px）",
    "EXIF ExifImageLength":      "画像の高さ（px）",
    "Image XResolution":         "横解像度",
    "Image YResolution":         "縦解像度",
    "Image ResolutionUnit":      "解像度の単位",
    "Image Orientation":         "画像の向き",
    "Image Software":            "ソフトウェア",
    "GPS GPSLatitude":           "撮影場所（緯度）",
    "GPS GPSLongitude":          "撮影場所（経度）",
    "GPS GPSAltitude":           "撮影高度",
}

# 技術的な内部データで表示不要なフィールド
HIDDEN_FIELDS = {
    "Image ExifOffset", "Image GPSInfo", "Image JPEGInterchangeFormat",
    "Image JPEGInterchangeFormatLength", "EXIF MakerNote",
    "EXIF ExifVersion", "EXIF FlashPixVersion",
    "EXIF ComponentsConfiguration", "EXIF SubSecTimeOriginal",
    "EXIF SubSecTime", "EXIF SubSecTimeDigitized", "Thumbnail Compression",
    "Thumbnail JPEGInterchangeFormat", "Thumbnail JPEGInterchangeFormatLength",
    "Thumbnail ResolutionUnit", "Thumbnail XResolution", "Thumbnail YResolution",
    "Thumbnail Orientation",
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

        # 既知フィールドは日本語ラベルで表示、技術的内部フィールドは非表示
        metadata = {}
        for field, label in CAMERA_FIELD_LABELS.items():
            if field in raw_tags:
                metadata[label] = raw_tags[field]
        for field, value in raw_tags.items():
            if field not in CAMERA_FIELD_LABELS and field not in HIDDEN_FIELDS:
                metadata[field] = value

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
