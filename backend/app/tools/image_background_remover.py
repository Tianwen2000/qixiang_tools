"""文件说明：实现「图片抠图」工具的后端逻辑。"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

from app.utils.image_utils import load_image, save_image


TOOL_META = {
    "slug": "image-background-remover",
    "name": "图片抠图",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}

_STRENGTH_PRESETS = {
    "gentle": {"low": 16, "high": 58, "edge_keep": 24, "blur": 0.95, "padding": 16, "neutral": 56},
    "standard": {"low": 24, "high": 74, "edge_keep": 20, "blur": 0.8, "padding": 12, "neutral": 68},
    "strong": {"low": 34, "high": 94, "edge_keep": 16, "blur": 0.65, "padding": 10, "neutral": 82},
}


def _sample_background_color(image: Image.Image) -> tuple[float, float, float]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    sample = max(8, min(width, height) // 12)
    boxes = [
        (0, 0, sample, sample),
        (width - sample, 0, width, sample),
        (0, height - sample, sample, height),
        (width - sample, height - sample, width, height),
    ]
    samples: list[tuple[int, int, int]] = []
    for left, top, right, bottom in boxes:
        region = rgba.crop((left, top, right, bottom))
        for red, green, blue, alpha in region.getdata():
            if alpha <= 0:
                continue
            samples.append((red, green, blue))
    if not samples:
        return 255.0, 255.0, 255.0
    values = np.array(samples, dtype=np.float32)
    red, green, blue = np.median(values, axis=0)
    return float(red), float(green), float(blue)


def _distance_to_background(pixel: tuple[int, int, int, int], background: tuple[float, float, float]) -> float:
    red, green, blue, _ = pixel
    return ((red - background[0]) ** 2 + (green - background[1]) ** 2 + (blue - background[2]) ** 2) ** 0.5


def _trim_transparent_border(image: Image.Image, padding: int) -> Image.Image:
    bbox = image.getbbox()
    if not bbox:
        return image
    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(image.width, right + padding)
    bottom = min(image.height, bottom + padding)
    return image.crop((left, top, right, bottom))


def _normalize_alpha_edges(image: Image.Image) -> Image.Image:
    alpha_mask = image.getchannel("A")
    cleaned_alpha = alpha_mask.load()
    for y in range(image.height):
        for x in range(image.width):
            alpha = cleaned_alpha[x, y]
            if alpha < 22:
                cleaned_alpha[x, y] = 0
            elif alpha > 246:
                cleaned_alpha[x, y] = 255
    image.putalpha(alpha_mask)
    return image


def _has_meaningful_transparency(image: Image.Image) -> bool:
    if "A" not in image.getbands():
        return False
    alpha = np.asarray(image.convert("RGBA").getchannel("A"), dtype=np.uint8)
    transparent_ratio = float(np.count_nonzero(alpha < 8)) / float(alpha.size)
    soft_edge_ratio = float(np.count_nonzero((alpha > 8) & (alpha < 248))) / float(alpha.size)
    return transparent_ratio > 0.005 or soft_edge_ratio > 0.01


def _preserve_existing_alpha(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = np.asarray(rgba.getchannel("A"), dtype=np.uint8)
    pixels = np.asarray(rgba, dtype=np.uint8).copy()
    pixels[alpha == 0, :3] = 0
    return Image.fromarray(pixels)


def _background_distance_map(rgba: Image.Image, background: tuple[float, float, float]) -> np.ndarray:
    rgb = np.asarray(rgba.convert("RGB"), dtype=np.float32)
    bg = np.array(background, dtype=np.float32).reshape(1, 1, 3)
    return np.linalg.norm(rgb - bg, axis=2)


def _rgb_stats(rgba: Image.Image) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rgb = np.asarray(rgba.convert("RGB"), dtype=np.float32)
    luma = rgb[:, :, 0] * 0.299 + rgb[:, :, 1] * 0.587 + rgb[:, :, 2] * 0.114
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    return rgb, luma, chroma


def _edge_connected_mask(candidate_mask: np.ndarray) -> np.ndarray:
    height, width = candidate_mask.shape
    flood_source = (candidate_mask.astype("uint8") * 255).copy()
    flood_mask = np.zeros((height + 2, width + 2), np.uint8)

    for x in range(width):
        if flood_source[0, x]:
            cv2.floodFill(flood_source, flood_mask, (x, 0), 128)
        if flood_source[height - 1, x]:
            cv2.floodFill(flood_source, flood_mask, (x, height - 1), 128)
    for y in range(height):
        if flood_source[y, 0]:
            cv2.floodFill(flood_source, flood_mask, (0, y), 128)
        if flood_source[y, width - 1]:
            cv2.floodFill(flood_source, flood_mask, (width - 1, y), 128)

    return flood_source == 128


def _remove_tiny_alpha_noise(alpha: np.ndarray, min_area: int) -> np.ndarray:
    foreground = (alpha > 10).astype("uint8")
    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(foreground, connectivity=8)
    cleaned = alpha.copy()
    for label in range(1, component_count):
        if stats[label, cv2.CC_STAT_AREA] < min_area:
            cleaned[labels == label] = 0
    return cleaned


def _build_background_model(rgba: Image.Image, config: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    background = _sample_background_color(rgba)
    rgb, luma, chroma = _rgb_stats(rgba)
    bg_luma = float(background[0] * 0.299 + background[1] * 0.587 + background[2] * 0.114)
    bg_chroma = float(max(background) - min(background))
    distance = _background_distance_map(rgba, background)
    neutral_limit = config["neutral"]

    candidate_background = distance <= config["high"]
    if bg_luma < 96:
        # 深色背景上的发光 Logo 容易残留黑灰脏边；低饱和、低亮度区域应更积极地判为背景。
        dark_neutral_background = (luma <= 150) & (chroma <= neutral_limit)
        near_black_background = luma <= 48
        candidate_background = candidate_background | dark_neutral_background | near_black_background
    elif bg_luma > 176 and bg_chroma < 42:
        # 白底/浅底图常有 JPEG 压缩产生的浅灰边，低饱和高亮区域也作为背景候选。
        light_neutral_background = (luma >= 138) & (chroma <= neutral_limit)
        candidate_background = candidate_background | light_neutral_background
    elif bg_chroma < 42:
        neutral_background = (np.abs(luma - bg_luma) <= config["high"] * 1.35) & (chroma <= neutral_limit)
        candidate_background = candidate_background | neutral_background

    connected_background = _edge_connected_mask(candidate_background)
    return rgb, luma, chroma, distance, connected_background


def _alpha_from_background_model(
    rgba: Image.Image,
    config: dict,
    luma: np.ndarray,
    chroma: np.ndarray,
    distance: np.ndarray,
    connected_background: np.ndarray,
) -> Image.Image:
    background = _sample_background_color(rgba)
    bg_luma = float(background[0] * 0.299 + background[1] * 0.587 + background[2] * 0.114)

    alpha = np.full(distance.shape, 255, dtype=np.float32)
    transition = np.clip((distance - config["low"]) / max(1.0, config["high"] - config["low"]), 0.0, 1.0)
    background_alpha = transition

    if bg_luma < 96:
        neutral_progress = np.clip((luma - 38) / 118, 0.0, 1.0)
        chroma_progress = np.clip(chroma / max(1.0, config["neutral"]), 0.0, 1.0)
        background_alpha = np.minimum(background_alpha, np.maximum(neutral_progress, chroma_progress) * 0.92)
    elif bg_luma > 176:
        light_progress = np.clip((248 - luma) / 95, 0.0, 1.0)
        chroma_progress = np.clip(chroma / max(1.0, config["neutral"]), 0.0, 1.0)
        background_alpha = np.minimum(background_alpha, np.maximum(light_progress, chroma_progress))

    alpha[connected_background] = background_alpha[connected_background] * 255.0

    original_alpha = np.asarray(rgba.getchannel("A"), dtype=np.float32)
    alpha = np.minimum(alpha, original_alpha)
    min_area = max(16, int(rgba.width * rgba.height * 0.00008))
    alpha = _remove_tiny_alpha_noise(alpha, min_area=min_area)
    alpha_mask = Image.fromarray(alpha.astype("uint8")).filter(ImageFilter.GaussianBlur(radius=config["blur"]))
    alpha_mask = alpha_mask.filter(ImageFilter.MedianFilter(size=3))
    return alpha_mask


def _build_color_alpha_mask(rgba: Image.Image, config: dict) -> tuple[Image.Image, np.ndarray, np.ndarray, np.ndarray]:
    _, luma, chroma, distance, connected_background = _build_background_model(rgba, config=config)
    background = np.array(_sample_background_color(rgba), dtype=np.float32)
    alpha_mask = _alpha_from_background_model(
        rgba,
        config=config,
        luma=luma,
        chroma=chroma,
        distance=distance,
        connected_background=connected_background,
    )
    return alpha_mask, connected_background, distance, np.array(background, dtype=np.float32)


def _decontaminate_edges(rgba: Image.Image, alpha_mask: Image.Image, background: np.ndarray) -> Image.Image:
    rgb = np.asarray(rgba.convert("RGB"), dtype=np.float32)
    alpha = np.asarray(alpha_mask, dtype=np.float32) / 255.0
    corrected = rgb.copy()
    edge = (alpha > 0.04) & (alpha < 0.96)
    if np.any(edge):
        safe_alpha = np.clip(alpha[edge], 0.08, 1.0).reshape(-1, 1)
        corrected_edge = (rgb[edge] - background.reshape(1, 3) * (1.0 - safe_alpha)) / safe_alpha
        corrected[edge] = np.clip(corrected_edge, 0, 255)
    return Image.fromarray(corrected.astype("uint8")).convert("RGBA")


def _apply_alpha_mask(rgba: Image.Image, alpha_mask: Image.Image, background: np.ndarray | None = None) -> Image.Image:
    output = _decontaminate_edges(rgba, alpha_mask, background) if background is not None else rgba.copy()
    output.putalpha(alpha_mask)
    return _normalize_alpha_edges(output)


def _transparent_ratio(image: Image.Image) -> float:
    alpha = np.asarray(image.convert("RGBA").getchannel("A"), dtype=np.uint8)
    return float(np.count_nonzero(alpha < 16)) / float(alpha.size)


def _simple_cutout(image: Image.Image, config: dict) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha_mask, _, _, background = _build_color_alpha_mask(rgba, config=config)
    return _apply_alpha_mask(rgba, alpha_mask, background=background)


def _smart_cutout(image: Image.Image, config: dict, strength: str) -> Image.Image:
    rgba = image.convert("RGBA")
    rgb = np.array(rgba.convert("RGB"))
    height, width = rgb.shape[:2]
    color_alpha_mask, connected_background, distance, background = _build_color_alpha_mask(rgba, config=config)

    mask = np.full((height, width), cv2.GC_PR_BGD, np.uint8)
    border = max(4, min(width, height) // 28)
    mask[:border, :] = cv2.GC_BGD
    mask[-border:, :] = cv2.GC_BGD
    mask[:, :border] = cv2.GC_BGD
    mask[:, -border:] = cv2.GC_BGD
    mask[connected_background] = cv2.GC_BGD
    mask[(~connected_background) & (distance >= config["high"])] = cv2.GC_PR_FGD
    mask[(~connected_background) & (distance >= config["high"] * 1.45)] = cv2.GC_FGD

    inset_x = max(border + 2, width // 14)
    inset_y = max(border + 2, height // 14)
    rect = (
        inset_x,
        inset_y,
        max(2, width - inset_x * 2),
        max(2, height - inset_y * 2),
    )

    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    iterations = {"gentle": 4, "standard": 5, "strong": 7}.get(strength, 5)

    has_foreground_seed = np.any((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD))
    try:
        if has_foreground_seed:
            cv2.grabCut(rgb, mask, None, bgd_model, fgd_model, iterations, cv2.GC_INIT_WITH_MASK)
        else:
            cv2.grabCut(rgb, mask, rect, bgd_model, fgd_model, iterations, cv2.GC_INIT_WITH_RECT)
    except cv2.error:
        return _simple_cutout(rgba, config=config)

    foreground_mask = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD),
        255,
        0,
    ).astype("uint8")

    kernel_size = max(3, (min(width, height) // 180) * 2 + 1)
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    edge_background = _edge_connected_mask(foreground_mask == 0)
    foreground_mask = np.where(edge_background, 0, 255).astype("uint8")
    foreground_mask = cv2.GaussianBlur(foreground_mask, (0, 0), sigmaX=max(1.0, config["blur"] * 1.8))
    foreground_mask = cv2.medianBlur(foreground_mask, 3)

    alpha = foreground_mask.astype(np.float32)
    color_alpha = np.asarray(color_alpha_mask, dtype=np.float32)
    alpha[connected_background] = np.minimum(alpha[connected_background], color_alpha[connected_background])
    original_alpha = np.asarray(rgba.getchannel("A"), dtype=np.float32)
    alpha = np.minimum(alpha, original_alpha)
    min_area = max(16, int(width * height * 0.00008))
    alpha = _remove_tiny_alpha_noise(alpha, min_area=min_area)

    output = _apply_alpha_mask(rgba, Image.fromarray(alpha.astype("uint8")), background=background)
    if _transparent_ratio(output) < 0.02:
        return _simple_cutout(rgba, config=config)
    return output


def _build_checkerboard(size: tuple[int, int], tile_size: int = 16) -> Image.Image:
    width, height = size
    board = Image.new("RGBA", size, (255, 255, 255, 255))
    pixels = board.load()
    light = (255, 255, 255, 255)
    dark = (214, 214, 214, 255)
    for y in range(height):
        for x in range(width):
            tile_x = x // tile_size
            tile_y = y // tile_size
            pixels[x, y] = light if (tile_x + tile_y) % 2 == 0 else dark
    return board


def _apply_output_background(image: Image.Image, output_background: str) -> tuple[Image.Image, str, str]:
    normalized = str(output_background).strip().lower()
    if normalized == "checkerboard":
        preview = Image.alpha_composite(_build_checkerboard(image.size), image.convert("RGBA"))
        return preview.convert("RGBA"), "image-cutout-checkerboard.png", "PNG"
    return image.convert("RGBA"), "image-cutout-transparent.png", "PNG"


def run(
    input_path: str,
    output_dir: str,
    mode: str = "simple",
    strength: str = "standard",
    output_background: str = "transparent",
    trim_border: str = "yes",
    **_: dict,
) -> str:
    config = _STRENGTH_PRESETS.get(str(strength).strip().lower(), _STRENGTH_PRESETS["standard"])
    image = load_image(input_path).convert("RGBA")

    if _has_meaningful_transparency(image):
        cutout = _preserve_existing_alpha(image)
    elif str(mode).strip().lower() == "smart":
        cutout = _smart_cutout(image, config=config, strength=strength)
    else:
        cutout = _simple_cutout(image, config=config)

    if str(trim_border).strip().lower() in {"yes", "true", "1"}:
        cutout = _trim_transparent_border(cutout, padding=config["padding"])

    final_image, filename, image_format = _apply_output_background(cutout, output_background=output_background)
    target_path = Path(output_dir) / filename
    return save_image(final_image, target_path, image_format)
