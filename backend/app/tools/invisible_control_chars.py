import unicodedata


TOOL_META = {
    "slug": "invisible-control-chars",
    "name": "隐形控制字符串打印",
    "category": "ops",
    "input_mode": "text",
    "result_type": "text",
}


INVISIBLE_CHARS = [
    ("高危 JS 控制符", "\u2028"),
    ("高危 JS 控制符", "\u2029"),
    ("零宽类", "\u200b"),
    ("零宽类", "\u200c"),
    ("零宽类", "\u200d"),
    ("零宽类", "\u2060"),
    ("BOM / 特殊空格", "\ufeff"),
    ("NULL", "\x00"),
    ("双向文本控制符", "\u202a"),
    ("双向文本控制符", "\u202b"),
    ("双向文本控制符", "\u202c"),
    ("双向文本控制符", "\u202d"),
    ("双向文本控制符", "\u202e"),
    ("C0 控制符", "\x01"),
    ("C0 控制符", "\x02"),
    ("C0 控制符", "\x03"),
    ("C0 控制符", "\x04"),
    ("C0 控制符", "\x05"),
    ("C0 控制符", "\x06"),
    ("C0 控制符", "\x07"),
    ("C0 控制符", "\x08"),
    ("C0 控制符", "\x09"),
    ("C0 控制符", "\x0a"),
    ("C0 控制符", "\x0b"),
    ("C0 控制符", "\x0c"),
    ("C0 控制符", "\x0d"),
    ("C0 控制符", "\x0e"),
    ("C0 控制符", "\x0f"),
    ("C1 控制符", "\x80"),
    ("C1 控制符", "\x81"),
    ("C1 控制符", "\x82"),
    ("C1 控制符", "\x83"),
    ("C1 控制符", "\x84"),
    ("C1 控制符", "\x85"),
    ("C1 控制符", "\x86"),
    ("C1 控制符", "\x87"),
    ("C1 控制符", "\x88"),
    ("C1 控制符", "\x89"),
    ("C1 控制符", "\x8a"),
    ("C1 控制符", "\x8b"),
    ("C1 控制符", "\x8c"),
    ("C1 控制符", "\x8d"),
    ("C1 控制符", "\x8e"),
    ("C1 控制符", "\x8f"),
]


def _unicode_name(char: str) -> str:
    try:
        return unicodedata.name(char)
    except ValueError:
        return "(no name)"


def _join_raw_chars(joiner: str) -> str:
    separators = {
        "none": "",
        "comma": "、",
        "newline": "\n",
    }
    return separators.get(joiner, "").join(char for _, char in INVISIBLE_CHARS)


def _build_table() -> str:
    lines = [
        f"{'Group':<18} | {'Unicode':<10} | {'Name':<35} | Repr",
        "-" * 88,
    ]
    for group, char in INVISIBLE_CHARS:
        code_point = f"U+{ord(char):04X}"
        lines.append(f"{group:<18} | {code_point:<10} | {_unicode_name(char):<35} | {repr(char)}")
    return "\n".join(lines)


def run(text: str = "", output_mode: str = "table_and_raw", joiner: str = "none", **_: dict) -> str:
    raw_line = _join_raw_chars(joiner)
    if output_mode == "raw_only":
        return f"{raw_line}以上是所有的不可见字符"

    return "\n\n".join(
        [
            _build_table(),
            "所有 Raw Char：",
            f"{raw_line}以上是所有的不可见字符",
        ]
    )
