from pathlib import Path

from PIL import Image

from app.core.exceptions import AppException
from app.utils.image_utils import extract_zip_to_dir, image_extension_from_format, list_image_files, load_image, save_image


TOOL_META = {
    "slug": "image-merger",
    "name": "图片拼接",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, direction: str = "vertical", gap: int = 0, output_format: str = "png", **_: dict) -> str:
    extracted = extract_zip_to_dir(input_path, Path(output_dir) / "merge-src")
    image_paths = list_image_files(extracted)
    if len(image_paths) < 2:
        raise AppException(message="请上传至少包含 2 张图片的 zip 压缩包", code=4002, status_code=400)

    images = [load_image(path).convert("RGBA") for path in sorted(image_paths)]
    gap = max(0, int(gap))
    if direction == "vertical":
        width = max(image.width for image in images)
        height = sum(image.height for image in images) + gap * (len(images) - 1)
        canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        offset = 0
        for image in images:
            canvas.alpha_composite(image, ((width - image.width) // 2, offset))
            offset += image.height + gap
    elif direction == "horizontal":
        width = sum(image.width for image in images) + gap * (len(images) - 1)
        height = max(image.height for image in images)
        canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        offset = 0
        for image in images:
            canvas.alpha_composite(image, (offset, (height - image.height) // 2))
            offset += image.width + gap
    else:
        raise AppException(message="不支持的拼接方向", code=4001, status_code=400)

    suffix = image_extension_from_format(output_format)
    target_path = Path(output_dir) / f"merged.{suffix}"
    format_name = "JPEG" if suffix == "jpg" else suffix.upper()
    return save_image(canvas, target_path, format_name)
