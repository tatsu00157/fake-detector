import io
import base64
import cv2
import numpy as np
from PIL import Image
from .base import error_result


def analyze(image_bytes: bytes) -> dict:
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return error_result("画像のデコードに失敗しました")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        vis = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).copy()
        for x, y, w, h in faces:
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 220, 100), 2)

        out = io.BytesIO()
        Image.fromarray(vis).save(out, format="PNG")
        vis_b64 = base64.b64encode(out.getvalue()).decode()

        return {
            "score": 0.0,
            "label": "info",
            "details": {
                "検出された顔の数": len(faces),
                "解説": "画像内で検出された顔を緑のボックスで囲んでいます",
            },
            "image": f"data:image/png;base64,{vis_b64}",
        }
    except Exception as e:
        return error_result(str(e))
