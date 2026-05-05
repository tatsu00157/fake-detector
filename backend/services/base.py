def get_label(score: float) -> str:
    if score < 0.3:
        return "clean"
    elif score < 0.6:
        return "warning"
    return "suspicious"


def error_result(message: str) -> dict:
    return {
        "score": 0.0,
        "label": "error",
        "details": {"error": message},
        "image": None,
    }
