"""文件说明：实现「JSON 格式化」工具的后端逻辑。"""

import json
import re

import json5

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "json-format",
    "name": "JSON 格式化",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, indent: int = 2, sort_keys: bool = False, action: str = "format", **_: dict) -> str:
    normalized_text = _normalize_json_like_text(text)

    if action == "validate":
        return _validate_strict_json(normalized_text)

    if action != "format":
        raise AppException(message="功能类型无效", code=4001, status_code=400)

    try:
        parsed = _parse_json_like_text(normalized_text)
    except ValueError as exc:
        raise AppException(message=f"JSON 格式无效：{exc}", code=4001, status_code=400) from exc

    if indent not in {2, 4}:
        raise AppException(message="缩进只能是 2 或 4", code=4001, status_code=400)

    return json.dumps(parsed, ensure_ascii=False, indent=indent, sort_keys=sort_keys)


def _normalize_json_like_text(text: str) -> str:
    normalized = text.strip().replace("\ufeff", "")
    if normalized.startswith("```") and normalized.endswith("```"):
        lines = normalized.splitlines()
        if len(lines) >= 3:
            normalized = "\n".join(lines[1:-1]).strip()
    return normalized


def _parse_json_like_text(text: str):
    if not text:
        raise ValueError("请输入 JSON 或类 JSON 内容")

    last_error: Exception | None = None
    for candidate in _build_candidate_texts(text):
        try:
            return json.loads(candidate)
        except Exception as exc:
            last_error = exc
        try:
            return json5.loads(candidate)
        except Exception as exc:
            last_error = exc

    try:
        repaired = _repair_json_like_text(text)
        return json5.loads(repaired)
    except Exception as exc:
        last_error = exc

    if last_error is None:
        raise ValueError("未识别到可解析的 JSON 片段")

    message = str(last_error).strip() or "内容不符合 JSON 结构"
    raise ValueError(re.sub(r"\s+", " ", message))


def _validate_strict_json(text: str) -> str:
    if not text:
        return "校验结果：不通过\n原因：请输入需要校验的 JSON 内容。"

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        detail = f"校验结果：不通过\n原因：{exc.msg}"
        if exc.lineno and exc.colno:
            detail += f"\n位置：第 {exc.lineno} 行，第 {exc.colno} 列"
        return detail

    preview = json.dumps(parsed, ensure_ascii=False, indent=2)
    return f"校验结果：通过\n说明：输入内容是有效 JSON。\n\n格式化预览：\n{preview}"


def _build_candidate_texts(text: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()

    def add_candidate(value: str) -> None:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            return
        seen.add(cleaned)
        candidates.append(cleaned)

    add_candidate(text)

    for marker in ("{", "["):
        for start_index, char in enumerate(text):
            if char != marker:
                continue
            end_index = _find_balanced_end(text, start_index)
            if end_index != -1:
                add_candidate(text[start_index : end_index + 1])

    colon_lines = [line.strip() for line in text.splitlines() if ":" in line]
    if colon_lines:
        add_candidate("{\n" + "\n".join(colon_lines) + "\n}")

    return candidates


def _repair_json_like_text(text: str) -> str:
    object_candidate = None
    for candidate in _build_candidate_texts(text):
        if candidate.startswith("{") and candidate.endswith("}"):
            object_candidate = candidate
            break
    source = object_candidate or text
    repaired = _repair_relaxed_object(source)
    if repaired is None:
        raise ValueError("未找到可修复的 JSON 结构")
    return repaired


def _repair_relaxed_object(text: str) -> str | None:
    lines = text.splitlines()
    result_lines: list[str] = []
    object_started = False
    pending_key_line = False
    current_key_prefix = ""
    current_quote = '"'
    current_multiline_parts: list[str] = []

    key_line_pattern = re.compile(r'^\s*(?P<prefix>(?:"[^"]+"|\'[^\']+\'|[A-Za-z0-9_\-\u4e00-\u9fff]+)\s*:\s*)(?P<value>.*?)(?P<comma>,?)\s*$')

    def normalize_key_prefix(prefix: str) -> str:
        key, _sep, _rest = prefix.partition(":")
        key = key.strip()
        if key.startswith('"') and key.endswith('"'):
            normalized_key = key
        elif key.startswith("'") and key.endswith("'"):
            normalized_key = json.dumps(key[1:-1], ensure_ascii=False)
        else:
            normalized_key = json.dumps(key, ensure_ascii=False)
        return f"{normalized_key}: "

    def finalize_multiline(add_comma: bool) -> None:
        nonlocal current_key_prefix, current_multiline_parts, current_quote
        merged = "\n".join(current_multiline_parts).rstrip()
        result_lines.append(f"{current_key_prefix}{json.dumps(merged, ensure_ascii=False)}{',' if add_comma else ''}")
        current_key_prefix = ""
        current_multiline_parts = []
        current_quote = '"'

    def strip_wrapped_string(raw: str) -> str:
        raw = raw.strip()
        if len(raw) >= 2 and raw[0] in {'"', "'"} and raw[-1] == raw[0]:
            try:
                return json5.loads(raw)
            except Exception:
                return raw[1:-1]
        return raw

    def convert_single_line_value(raw_value: str) -> str:
        raw = raw_value.strip().rstrip(",").strip()
        if not raw:
            return '""'
        if raw[0] in "{[":
            return raw
        if raw in {"true", "false", "null"} or re.fullmatch(r"-?\d+(?:\.\d+)?", raw):
            return raw
        if len(raw) >= 2 and raw[0] in {'"', "'"} and raw[-1] == raw[0]:
            try:
                parsed = json5.loads(raw)
                return json.dumps(parsed, ensure_ascii=False)
            except Exception:
                return json.dumps(raw[1:-1], ensure_ascii=False)
        return json.dumps(raw, ensure_ascii=False)

    def is_multiline_end(line: str, quote_char: str) -> bool:
        stripped = line.rstrip()
        return bool(re.search(rf'(?<!\\){re.escape(quote_char)}\s*,?\s*$', stripped))

    def trim_multiline_end(line: str, quote_char: str) -> str:
        return re.sub(rf'(?<!\\){re.escape(quote_char)}\s*,?\s*$', "", line.rstrip())

    for raw_line in lines:
        stripped = raw_line.strip()

        if not object_started and "{" in stripped:
            object_started = True
            result_lines.append("{")
            tail = stripped[stripped.find("{") + 1 :].strip()
            if not tail:
                continue
            stripped = tail
            raw_line = tail

        if current_multiline_parts:
            if is_multiline_end(raw_line, current_quote):
                current_multiline_parts.append(trim_multiline_end(raw_line, current_quote))
                finalize_multiline(add_comma=True)
                continue
            if stripped in {"}", "},"} or key_line_pattern.match(raw_line):
                finalize_multiline(add_comma=stripped not in {"}", "},"})
                if stripped in {"}", "},"}:
                    if result_lines and result_lines[-1].endswith(","):
                        result_lines[-1] = result_lines[-1].rstrip(",")
                    result_lines.append("}")
                    object_started = False
                    continue
            else:
                current_multiline_parts.append(raw_line.rstrip())
                continue

        if stripped in {"", ","}:
            continue

        if stripped in {"}", "},"}:
            if result_lines and result_lines[-1].endswith(","):
                result_lines[-1] = result_lines[-1].rstrip(",")
            result_lines.append("}")
            object_started = False
            continue

        match = key_line_pattern.match(raw_line)
        if not match:
            continue

        object_started = True
        prefix = normalize_key_prefix(match.group("prefix"))
        value = match.group("value").strip()
        has_comma = match.group("comma") == ","

        if value and value[0] in {'"', "'"}:
            quote_char = value[0]
            tail = value[1:]
            if is_multiline_end(tail, quote_char):
                single_value = strip_wrapped_string(value.rstrip(","))
                result_lines.append(f"{prefix}{json.dumps(single_value, ensure_ascii=False)}{',' if has_comma else ''}")
            else:
                current_key_prefix = prefix
                current_quote = quote_char
                current_multiline_parts = [tail.rstrip()]
            continue

        result_lines.append(f"{prefix}{convert_single_line_value(value)}{',' if has_comma else ''}")

    if current_multiline_parts:
        finalize_multiline(add_comma=False)

    if not result_lines:
        return None

    if result_lines[-1] != "}":
        if result_lines and result_lines[-1].endswith(","):
            result_lines[-1] = result_lines[-1].rstrip(",")
        result_lines.append("}")

    return "\n".join(result_lines)


def _find_balanced_end(text: str, start_index: int) -> int:
    stack = [text[start_index]]
    in_string = False
    string_char = ""
    escape = False

    for index in range(start_index + 1, len(text)):
        char = text[index]

        if in_string:
            if escape:
                escape = False
                continue
            if char == "\\":
                escape = True
                continue
            if char == string_char:
                in_string = False
            continue

        if char in {'"', "'"}:
            in_string = True
            string_char = char
            continue

        if char == "{":
            stack.append("{")
            continue

        if char == "[":
            stack.append("[")
            continue

        if char == "}" and stack and stack[-1] == "{":
            stack.pop()
            if not stack:
                return index
            continue

        if char == "]" and stack and stack[-1] == "[":
            stack.pop()
            if not stack:
                return index

    return -1
