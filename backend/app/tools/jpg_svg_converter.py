from app.tools.svg_image_converter import convert_svg_image


TOOL_META = {
    "slug": "jpg-svg-converter",
    "name": "JPG 和 SVG 互转",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, direction: str = "jpg_to_svg", **_: dict) -> str:
    return convert_svg_image(input_path, output_dir, direction, "jpg")
