"""文件说明：实现「PNG、JPG 和 ICO 互转」工具的后端逻辑。"""

from app.tools.icon_image_converter import convert_icon_image


TOOL_META = {
    "slug": "png-jpg-ico-converter",
    "name": "PNG、JPG 和 ICO 互转",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, direction: str = "png_to_ico", **_: dict) -> str:
    return convert_icon_image(input_path, output_dir, direction, "ico")
