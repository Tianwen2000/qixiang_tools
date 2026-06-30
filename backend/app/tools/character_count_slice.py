"""文件说明：实现「字符统计截取输出」工具的后端逻辑。"""

from collections import Counter
import unicodedata

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "character-count-slice",
    "name": "字符统计截取输出",
    "category": "ops",
    "input_mode": "text",
    "result_type": "text",
}


CONTROL_CATEGORY_PREFIXES = {"C"}
PUNCTUATION_CATEGORY_PREFIXES = {"P"}
SYMBOL_CATEGORY_PREFIXES = {"S"}


def _to_positive_int(value: object, default: int = 20) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise AppException(message="截取字符数必须是整数", code=4001, status_code=400) from exc
    return max(0, number)


def _char_label(char: str) -> str:
    aliases = {
        " ": "空格 SPACE",
        "\n": "换行 LF",
        "\r": "回车 CR",
        "\t": "制表符 TAB",
        "\f": "换页 FF",
        "\v": "垂直制表 VT",
        "\u3000": "全角空格 IDEOGRAPHIC SPACE",
        "\u00a0": "不换行空格 NO-BREAK SPACE",
    }
    if char in aliases:
        return aliases[char]
    name = unicodedata.name(char, "UNKNOWN")
    visible = char if not char.isspace() and not unicodedata.category(char).startswith("C") else repr(char)
    return f"{visible} {name}"


def _unicode_code(char: str) -> str:
    return f"U+{ord(char):04X}"


def _category_label(char: str) -> str:
    if char.isspace():
        return "空白字符"
    prefix = unicodedata.category(char)[0]
    if prefix in CONTROL_CATEGORY_PREFIXES:
        return "控制/格式字符"
    if prefix in PUNCTUATION_CATEGORY_PREFIXES:
        return "标点字符"
    if prefix in SYMBOL_CATEGORY_PREFIXES:
        return "符号/Emoji"
    return "普通字符"


def _is_special(char: str) -> bool:
    return _category_label(char) != "普通字符"


def _format_special_details(counter: Counter[str]) -> list[str]:
    special_items = [(char, count) for char, count in counter.items() if _is_special(char)]
    if not special_items:
        return ["无"]

    lines = []
    for char, count in sorted(special_items, key=lambda item: (_category_label(item[0]), ord(item[0]))):
        lines.append(f"- {_char_label(char)}（{_unicode_code(char)}，{_category_label(char)}）：{count}")
    return lines


def run(text: str, slice_from: str = "front", slice_count: int = 20, **_: dict) -> str:
    if slice_from not in {"front", "back"}:
        raise AppException(message="截取方向不支持", code=4001, status_code=400)

    count = _to_positive_int(slice_count)
    chars = list(text)
    total_count = len(chars)
    char_counter = Counter(chars)
    category_counter = Counter(_category_label(char) for char in chars)
    special_count = sum(amount for char, amount in char_counter.items() if _is_special(char))
    normal_count = total_count - special_count

    if slice_from == "front":
        sliced_chars = chars[:count]
        slice_label = "最前"
    else:
        sliced_chars = chars[-count:] if count else []
        slice_label = "最后"
    sliced_text = "".join(sliced_chars)

    result_lines = [
        "字符统计",
        f"总字符数：{total_count}",
        f"普通字符数：{normal_count}",
        f"特殊/空白字符总数：{special_count}",
        f"空白字符数：{category_counter['空白字符']}",
        f"标点字符数：{category_counter['标点字符']}",
        f"符号/Emoji 数：{category_counter['符号/Emoji']}",
        f"控制/格式字符数：{category_counter['控制/格式字符']}",
        "",
        "特殊字符明细",
        *_format_special_details(char_counter),
        "",
        "截取输出",
        f"截取方向：{slice_label}",
        f"请求截取字符数：{count}",
        f"实际输出字符数：{len(sliced_chars)}",
        "输出内容：",
        sliced_text,
    ]
    return "\n".join(result_lines)
