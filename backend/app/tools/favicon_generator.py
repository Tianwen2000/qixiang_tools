"""文件说明：实现「在线生成 Favicon.ico」工具的后端逻辑。"""

from pathlib import Path

from app.utils.image_utils import load_image


TOOL_META = {
    "slug": "favicon-generator",
    "name": "在线生成 Favicon.ico",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, size: int = 64, **_: dict) -> str:
    image = load_image(input_path).convert("RGBA")
    target_size = max(16, int(size))
    resized = image.resize((target_size, target_size))
    target_path = Path(output_dir) / "favicon.ico"
    resized.save(target_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (target_size, target_size)])
    return str(target_path)
