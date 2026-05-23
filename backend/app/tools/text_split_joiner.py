from app.core.exceptions import AppException


TOOL_META = {
    "slug": "text-split-joiner",
    "name": "文本拆分合并",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


SEPARATOR_PRESETS = {
    "comma": ",",
    "cn_comma": "，",
    "space": " ",
    "pipe": "|",
    "tab": "\t",
    "custom": None,
}

OUTPUT_PRESETS = {
    "newline": "\n",
    "comma": ",",
    "cn_comma": "，",
    "space": " ",
    "pipe": "|",
    "tab": "\t",
    "custom": None,
}


def _resolve_separator(kind: str, custom_value: str, mapping: dict[str, str | None], label: str) -> str:
    if kind not in mapping:
        raise AppException(message=f"不支持的{label}", code=4001, status_code=400)
    if kind == "custom":
        if custom_value == "":
            raise AppException(message=f"请先输入自定义{label}", code=4001, status_code=400)
        return custom_value
    return mapping[kind] or ""


def run(
    text: str,
    action: str = "split_to_lines",
    input_separator: str = "comma",
    output_separator: str = "comma",
    custom_input_separator: str = "",
    custom_output_separator: str = "",
    trim_items: bool = True,
    remove_empty_items: bool = True,
    **_: dict,
) -> str:
    if action == "split_to_lines":
        separator = _resolve_separator(input_separator, custom_input_separator, SEPARATOR_PRESETS, "输入分隔符")
        items = text.split(separator)
        processed = []
        for item in items:
            current = item.strip() if trim_items else item
            if remove_empty_items and current == "":
                continue
            processed.append(current)
        return "\n".join(processed)

    if action == "join_lines":
        separator = _resolve_separator(output_separator, custom_output_separator, OUTPUT_PRESETS, "输出分隔符")
        items = text.splitlines()
        processed = []
        for item in items:
            current = item.strip() if trim_items else item
            if remove_empty_items and current == "":
                continue
            processed.append(current)
        return separator.join(processed)

    raise AppException(message="不支持的拆分合并方式", code=4001, status_code=400)
