from app.core.exceptions import AppException


TOOL_META = {
    "slug": "css-gradient-generator",
    "name": "CSS 渐变生成器",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def run(
    text: str = "",
    gradient_type: str = "linear",
    direction: str = "90deg",
    start_color: str = "#4facfe",
    end_color: str = "#00f2fe",
    **_: dict,
) -> str:
    _ = text
    if gradient_type == "linear":
        return f"background: linear-gradient({direction}, {start_color}, {end_color});"
    if gradient_type == "radial":
        return f"background: radial-gradient(circle at center, {start_color}, {end_color});"
    raise AppException(message="不支持的渐变类型", code=4001, status_code=400)
