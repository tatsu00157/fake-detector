import io
import json
from PIL import Image
from .base import get_label, error_result

AI_TOOLS = [
    "stable diffusion", "midjourney", "dall-e", "firefly",
    "adobe firefly", "openai", "runway", "sora", "kling",
    "imagen", "gemini", "ideogram", "leonardo",
]


def _check_xmp(img: Image.Image) -> dict | None:
    xmp = img.info.get("xmp") or img.info.get("XML:com.adobe.xmp", "")
    if not xmp:
        return None
    xmp_str = xmp.decode("utf-8", errors="ignore") if isinstance(xmp, bytes) else xmp
    xmp_lower = xmp_str.lower()
    for tool in AI_TOOLS:
        if tool in xmp_lower:
            return {"tool": tool.title(), "source": "XMP"}
    return None


def analyze(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        found = {}

        # C2PA
        try:
            import c2pa
            reader = c2pa.Reader("image/jpeg", io.BytesIO(image_bytes))
            manifest_json = reader.json()
            manifest = json.loads(manifest_json)
            active = manifest.get("active_manifest", "")
            manifests = manifest.get("manifests", {})
            if active and active in manifests:
                m = manifests[active]
                generator = m.get("claim_generator", "")
                title = m.get("title", "")
                found["c2pa"] = {"generator": generator, "title": title}
        except Exception:
            pass

        # XMP
        xmp_result = _check_xmp(img)
        if xmp_result:
            found["xmp"] = xmp_result

        if found:
            details = []
            if "c2pa" in found:
                g = found["c2pa"].get("generator", "")
                details.append(f"C2PA署名: {g}")
            if "xmp" in found:
                details.append(f"XMP署名: {found['xmp']['tool']}")
            return {
                "score": 1.0,
                "label": "suspicious",
                "details": {
                    "found": True,
                    "signatures": found,
                    "summary": " / ".join(details),
                    "note": "AI生成ツールの署名が検出されました",
                },
                "image": None,
            }

        return {
            "score": 0.0,
            "label": "clean",
            "details": {
                "found": False,
                "note": "AI生成ツールの署名は検出されませんでした",
            },
            "image": None,
        }

    except Exception as e:
        return error_result(str(e))
