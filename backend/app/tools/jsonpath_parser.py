import json

from app.core.exceptions import AppException
from app.utils.codegen_utils import load_json_value


TOOL_META = {
    "slug": "jsonpath-parser",
    "name": "JSONPath 解析器",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def _tokenize(path: str) -> list[tuple[str, str | int]]:
    expression = path.strip()
    if not expression or expression == "$":
        return []
    if not expression.startswith("$"):
        raise AppException(message="JSONPath 必须以 $ 开头", code=4001, status_code=400)

    tokens: list[tuple[str, str | int]] = []
    index = 1
    while index < len(expression):
        char = expression[index]
        if char == ".":
            index += 1
            if index < len(expression) and expression[index] == "*":
                tokens.append(("wildcard", "*"))
                index += 1
                continue
            start = index
            while index < len(expression) and expression[index] not in ".[":
                index += 1
            name = expression[start:index]
            if not name:
                raise AppException(message="JSONPath 片段无效", code=4001, status_code=400)
            tokens.append(("prop", name))
            continue
        if char == "[":
            end = expression.find("]", index)
            if end == -1:
                raise AppException(message="JSONPath 的方括号未闭合", code=4001, status_code=400)
            content = expression[index + 1 : end].strip()
            if content == "*":
                tokens.append(("wildcard", "*"))
            elif (content.startswith("'") and content.endswith("'")) or (content.startswith('"') and content.endswith('"')):
                tokens.append(("prop", content[1:-1]))
            else:
                try:
                    tokens.append(("index", int(content)))
                except ValueError as exc:
                    raise AppException(message="JSONPath 下标必须是整数", code=4001, status_code=400) from exc
            index = end + 1
            continue
        raise AppException(message="不支持的 JSONPath 语法", code=4001, status_code=400)
    return tokens


def _evaluate(data, tokens: list[tuple[str, str | int]]):
    current = [data]
    for kind, value in tokens:
        next_nodes = []
        for node in current:
            if kind == "prop" and isinstance(node, dict) and value in node:
                next_nodes.append(node[value])
            elif kind == "index" and isinstance(node, list):
                idx = int(value)
                if -len(node) <= idx < len(node):
                    next_nodes.append(node[idx])
            elif kind == "wildcard":
                if isinstance(node, dict):
                    next_nodes.extend(node.values())
                elif isinstance(node, list):
                    next_nodes.extend(node)
        current = next_nodes
    return current


def run(text: str, path: str = "$", **_: dict) -> str:
    parsed = load_json_value(text)
    matches = _evaluate(parsed, _tokenize(path or "$"))
    payload = {
        "path": path or "$",
        "match_count": len(matches),
        "matches": matches,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
