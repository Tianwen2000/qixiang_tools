from app.tools.gif_image_converter import convert_gif_image


TOOL_META = {
    "slug": "gif-jpg-converter",
    "name": "GIF / JPG 互转",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, direction: str = "gif_to_jpg", **_: dict) -> str:
    return convert_gif_image(input_path, output_dir, direction, "jpg")
