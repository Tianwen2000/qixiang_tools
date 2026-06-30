"""文件说明：实现「图片识别文字」工具的后端逻辑。"""

from functools import lru_cache

from app.core.exceptions import AppException

try:
    from rapidocr_onnxruntime import RapidOCR
except ImportError:  # pragma: no cover - 依赖由 requirements 管理
    RapidOCR = None


TOOL_META = {
    "slug": "image-text-recognizer",
    "name": "图片识别文字",
    "category": "image",
    "input_mode": "file",
    "result_type": "text",
}


@lru_cache(maxsize=1)
def get_engine() -> "RapidOCR":
    if RapidOCR is None:
        raise AppException(message="OCR 依赖未安装，请先安装 rapidocr_onnxruntime", code=5002, status_code=500)
    try:
        return RapidOCR()
    except Exception as exc:  # pragma: no cover - 初始化异常依赖运行环境
        raise AppException(message=f"OCR 引擎初始化失败：{exc}", code=5002, status_code=500) from exc


def run(input_path: str, **_: dict) -> str:
    try:
        result, _ = get_engine()(input_path)
    except AppException:
        raise
    except Exception as exc:
        raise AppException(message=f"图片识别失败：{exc}", code=5002, status_code=500) from exc

    if not result:
        raise AppException(message="未识别到可用文字", code=4002, status_code=400)

    rows: list[str] = []
    for item in result:
        if not item or len(item) < 2:
            continue
        text = str(item[1]).strip()
        if text:
            rows.append(text)

    if not rows:
        raise AppException(message="未识别到可用文字", code=4002, status_code=400)
    return "\n".join(rows)
