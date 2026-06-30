"""文件说明：实现「CSS 单位互转」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "css-unit-converter",
    "name": "CSS 单位互转",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def _to_float(value: str, label: str) -> float:
    try:
        return float(str(value).strip())
    except ValueError as exc:
        raise AppException(message=f"{label}无效", code=4001, status_code=400) from exc


def _to_px(value: float, from_unit: str, root_font_size: float, screen_width: float) -> float:
    if from_unit == "px":
        return value
    if from_unit == "rem":
        return value * root_font_size
    if from_unit == "rpx":
        return value * screen_width / 750
    raise AppException(message="不支持的源单位", code=4001, status_code=400)


def _from_px(value: float, to_unit: str, root_font_size: float, screen_width: float) -> float:
    if to_unit == "px":
        return value
    if to_unit == "rem":
        return value / root_font_size
    if to_unit == "rpx":
        return value * 750 / screen_width
    raise AppException(message="不支持的目标单位", code=4001, status_code=400)


def _format_number(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def run(
    text: str,
    from_unit: str = "px",
    to_unit: str = "rem",
    root_font_size: str = "16",
    screen_width: str = "375",
    **_: dict,
) -> str:
    value = _to_float(text, "输入值")
    root_size = _to_float(root_font_size, "根字号")
    width = _to_float(screen_width, "屏幕宽度")

    if root_size <= 0 or width <= 0:
        raise AppException(message="根字号和屏幕宽度必须大于 0", code=4001, status_code=400)

    px_value = _to_px(value, from_unit, root_size, width)
    converted = _from_px(px_value, to_unit, root_size, width)
    return f"{_format_number(converted)}{to_unit}"
