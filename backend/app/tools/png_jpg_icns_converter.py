from app.tools.icon_image_converter import convert_icon_image


TOOL_META = {
    "slug": "png-jpg-icns-converter",
    "name": "PNG、JPG 和 ICNS 互转",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, direction: str = "png_to_icns", **_: dict) -> str:
    return convert_icon_image(input_path, output_dir, direction, "icns")
