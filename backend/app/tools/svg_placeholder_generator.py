from pathlib import Path

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "svg-placeholder-generator",
    "name": "SVG 占位符生成器",
    "category": "image",
    "input_mode": "text",
    "result_type": "file",
}


def run(
    text: str,
    output_dir: str,
    width: int = 800,
    height: int = 450,
    background_color: str = "#dbeafe",
    text_color: str = "#1e3a8a",
    **_: dict,
) -> str:
    label = text.strip() or f"{width} x {height}"
    width = max(60, int(width))
    height = max(60, int(height))
    if not background_color.startswith("#") or not text_color.startswith("#"):
        raise AppException(message="颜色值必须使用十六进制格式", code=4001, status_code=400)

    font_size = max(18, min(width, height) // 8)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="{background_color}" rx="28" ry="28"/>
  <g fill="none" stroke="{text_color}" opacity="0.22">
    <circle cx="{width * 0.18:.0f}" cy="{height * 0.25:.0f}" r="{min(width, height) * 0.16:.0f}"/>
    <circle cx="{width * 0.84:.0f}" cy="{height * 0.72:.0f}" r="{min(width, height) * 0.2:.0f}"/>
  </g>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        fill="{text_color}" font-family="'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif"
        font-size="{font_size}" font-weight="700">{label}</text>
</svg>
"""
    target_path = Path(output_dir) / "placeholder.svg"
    target_path.write_text(svg, encoding="utf-8")
    return str(target_path)
