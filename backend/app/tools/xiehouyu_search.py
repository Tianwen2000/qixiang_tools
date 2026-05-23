import json
from pathlib import Path

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "xiehouyu-search",
    "name": "歇后语",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "xiehouyu.json"


def _load_items() -> list[dict]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def run(text: str, limit: int = 10, **_: dict) -> str:
    keyword = text.strip()
    if not keyword:
        raise AppException(message="请输入关键词或歇后语前半句", code=4001, status_code=400)
    if limit not in {5, 10, 20}:
        raise AppException(message="结果数量只能是 5、10 或 20", code=4001, status_code=400)

    matches = [
        item
        for item in _load_items()
        if keyword in item["front"] or keyword in item["back"] or keyword in item["meaning"]
    ][:limit]

    if not matches:
        return "未找到匹配的歇后语"
    return "\n".join(f"{item['front']} - {item['back']}  {item['meaning']}" for item in matches)
