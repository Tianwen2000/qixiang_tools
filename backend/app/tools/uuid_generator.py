import uuid

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "uuid-generator",
    "name": "UUID 生成器",
    "category": "utility",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str = "", version: str = "v4", count: int = 1, **_: dict) -> str:
    _ = text
    creators = {
        "v1": uuid.uuid1,
        "v4": uuid.uuid4,
    }
    if version not in creators:
        raise AppException(message="UUID 版本必须是 v1 或 v4", code=4001, status_code=400)
    if int(count) not in {1, 5, 10}:
        raise AppException(message="生成数量必须是 1、5 或 10", code=4001, status_code=400)
    return "\n".join(str(creators[version]()) for _ in range(int(count)))
