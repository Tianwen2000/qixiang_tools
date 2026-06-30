"""文件说明：实现「二维码解析」工具的后端逻辑。"""

import cv2

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "qr-code-decoder",
    "name": "二维码解析",
    "category": "image",
    "input_mode": "file",
    "result_type": "text",
}


def run(input_path: str, **_: dict) -> str:
    detector = cv2.QRCodeDetector()
    image = cv2.imread(input_path)
    if image is None:
        raise AppException(message="无法读取二维码图片", code=4002, status_code=400)
    value, _, _ = detector.detectAndDecode(image)
    if not value:
        raise AppException(message="未识别到二维码内容", code=4002, status_code=400)
    return value
