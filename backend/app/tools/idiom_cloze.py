import json
from pathlib import Path

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "idiom-cloze",
    "name": "成语填空",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "idioms.json"
PLACEHOLDERS = set("?？*＊_＿口◻□.")


def _load_idioms() -> list[dict]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def _normalize(text: str) -> str:
    return "".join(char for char in text.strip() if not char.isspace())


def _is_pattern(text: str) -> bool:
    return any(char in PLACEHOLDERS for char in text)


def _match_pattern(pattern: str, idiom_text: str) -> bool:
    if len(pattern) != len(idiom_text):
        return False
    return all(left == right or left in PLACEHOLDERS for left, right in zip(pattern, idiom_text))


def run(text: str, limit: int = 10, **_: dict) -> str:
    keyword = _normalize(text)
    if not keyword:
        raise AppException(message="请输入成语或填空题面", code=4001, status_code=400)
    if limit not in {5, 10, 20}:
        raise AppException(message="结果数量只能是 5、10 或 20", code=4001, status_code=400)

    matches: list[dict] = []
    for item in _load_idioms():
        idiom_text = item["idiom"]
        if _is_pattern(keyword):
            if _match_pattern(keyword, idiom_text):
                matches.append(item)
        elif keyword in idiom_text or keyword in item["meaning"]:
            matches.append(item)
        if len(matches) >= limit:
            break

    if not matches:
        return "未找到匹配的成语"

    return "\n".join(f"{item['idiom']}  {item['meaning']}" for item in matches)
