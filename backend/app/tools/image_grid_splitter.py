"""文件说明：实现「九宫格/多格切图」工具的后端逻辑。"""

from pathlib import Path

from app.core.exceptions import AppException
from app.utils.image_utils import IMAGE_FORMATS, load_image, save_image, zip_output_files


TOOL_META = {
    "slug": "image-grid-splitter",
    "name": "九宫格/多格切图",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, rows: int = 3, cols: int = 3, **_: dict) -> str:
    rows = int(rows)
    cols = int(cols)
    if rows <= 0 or cols <= 0:
        raise AppException(message="行列数必须大于 0", code=4001, status_code=400)

    image = load_image(input_path)
    piece_dir = Path(output_dir) / "grid"
    piece_dir.mkdir(parents=True, exist_ok=True)
    piece_width = image.width // cols
    piece_height = image.height // rows
    suffix = Path(input_path).suffix.lower().lstrip(".") or "png"
    target_format = IMAGE_FORMATS.get(suffix, "PNG")

    index = 1
    for row in range(rows):
        for col in range(cols):
            left = col * piece_width
            top = row * piece_height
            right = image.width if col == cols - 1 else (col + 1) * piece_width
            bottom = image.height if row == rows - 1 else (row + 1) * piece_height
            piece = image.crop((left, top, right, bottom))
            save_image(piece, piece_dir / f"grid-{index}.{suffix}", target_format)
            index += 1

    return zip_output_files(piece_dir, Path(output_dir) / "grid-split.zip")
