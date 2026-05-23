import re

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "color-converter",
    "name": "颜色选择器转换器",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


RGB_RE = re.compile(r"^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$", re.IGNORECASE)
RGBA_RE = re.compile(
    r"^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([01](?:\.\d+)?)\s*\)$",
    re.IGNORECASE,
)


def _parse_color(value: str) -> tuple[int, int, int, float]:
    text = value.strip()
    if text.startswith("#"):
        raw = text[1:]
        if len(raw) == 3:
            raw = "".join(char * 2 for char in raw)
        if len(raw) != 6:
            raise AppException(message="Hex 颜色值无效", code=4001, status_code=400)
        try:
            red = int(raw[0:2], 16)
            green = int(raw[2:4], 16)
            blue = int(raw[4:6], 16)
        except ValueError as exc:
            raise AppException(message="Hex 颜色值无效", code=4001, status_code=400) from exc
        return red, green, blue, 1.0

    rgba_match = RGBA_RE.match(text)
    if rgba_match:
        red, green, blue = (int(rgba_match.group(index)) for index in range(1, 4))
        alpha = float(rgba_match.group(4))
        return red, green, blue, alpha

    rgb_match = RGB_RE.match(text)
    if rgb_match:
        red, green, blue = (int(rgb_match.group(index)) for index in range(1, 4))
        return red, green, blue, 1.0

    raise AppException(message="不支持的颜色格式", code=4001, status_code=400)


def _format_alpha(alpha: float) -> str:
    text = f"{alpha:.4f}".rstrip("0").rstrip(".")
    return text or "0"


def run(text: str, to_format: str = "hex", **_: dict) -> str:
    red, green, blue, alpha = _parse_color(text)
    if to_format == "hex":
        return f"#{red:02X}{green:02X}{blue:02X}"
    if to_format == "rgb":
        return f"rgb({red}, {green}, {blue})"
    if to_format == "rgba":
        return f"rgba({red}, {green}, {blue}, {_format_alpha(alpha)})"
    raise AppException(message="不支持的颜色输出格式", code=4001, status_code=400)
