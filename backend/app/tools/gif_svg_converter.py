from app.tools.svg_image_converter import convert_svg_image


TOOL_META = {
    "slug": "gif-svg-converter",
    "name": "GIF 和 SVG 互转",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}


def run(
    input_path: str,
    output_dir: str,
    direction: str = "gif_to_svg",
    duration_seconds: object = 2,
    fps: object = 12,
    **_: dict,
) -> str:
    return convert_svg_image(
        input_path,
        output_dir,
        direction,
        "gif",
        duration_seconds=duration_seconds,
        fps=fps,
    )
