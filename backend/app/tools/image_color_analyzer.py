"""文件说明：实现「图片颜色分析」工具的后端逻辑。"""

from collections import Counter

from app.utils.image_utils import load_image


TOOL_META = {
    "slug": "image-color-analyzer",
    "name": "图片颜色分析",
    "category": "image",
    "input_mode": "file",
    "result_type": "text",
}


def run(input_path: str, top_n: int = 5, **_: dict) -> str:
    image = load_image(input_path).convert("RGB")
    sample = image.resize((120, 120))
    pixels = list(sample.getdata())
    counter = Counter(pixels)
    total = len(pixels)
    rows = [f"图片尺寸：{image.width} x {image.height}", f"分析颜色数：前 {top_n} 个"]
    for color, count in counter.most_common(max(1, int(top_n))):
        ratio = count / total * 100
        rows.append(f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}  RGB{color}  占比 {ratio:.2f}%")
    return "\n".join(rows)
