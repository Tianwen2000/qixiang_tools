import io
import zipfile
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

from app.core.exceptions import AppException


IMAGE_FORMATS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "bmp": "BMP",
    "gif": "GIF",
    "ico": "ICO",
    "tif": "TIFF",
    "tiff": "TIFF",
}

IMAGE_SUFFIXES = set(IMAGE_FORMATS)


def load_image(path: str | Path) -> Image.Image:
    try:
        image = Image.open(path)
        image.load()
        return image
    except Exception as exc:
        raise AppException(message=f"无法读取图片文件：{exc}", code=4002, status_code=400) from exc


def image_extension_from_format(output_format: str) -> str:
    normalized = output_format.strip().lower()
    if normalized == "jpeg":
        return "jpg"
    if normalized not in {"jpg", "png", "webp", "bmp", "gif", "ico", "tiff"}:
        raise AppException(message="不支持的图片格式", code=4001, status_code=400)
    return normalized


def make_output_path(output_dir: str | Path, filename: str, suffix: str) -> Path:
    target = Path(output_dir) / filename
    if not filename.endswith(f".{suffix}"):
        target = target.with_suffix(f".{suffix}")
    return target


def ensure_rgb(image: Image.Image, background: tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
    if image.mode in {"RGB", "L"}:
        return image.convert("RGB")
    if image.mode in {"RGBA", "LA"}:
        canvas = Image.new("RGBA", image.size, (*background, 255))
        canvas.alpha_composite(image.convert("RGBA"))
        return canvas.convert("RGB")
    return image.convert("RGB")


def save_image(
    image: Image.Image,
    target_path: Path,
    output_format: str,
    quality: int | None = None,
    preserve_animation: bool = False,
    frames: list[Image.Image] | None = None,
    durations: list[int] | None = None,
    loop: int = 0,
) -> str:
    normalized = output_format.upper()

    if preserve_animation and frames:
        frames[0].save(
            target_path,
            format=normalized,
            save_all=True,
            append_images=frames[1:],
            duration=durations or 120,
            loop=loop,
            optimize=False,
        )
        return str(target_path)

    save_kwargs: dict = {"format": normalized}
    if normalized in {"JPEG", "WEBP"} and quality is not None:
        save_kwargs["quality"] = max(1, min(int(quality), 95))
        save_kwargs["optimize"] = True
    if normalized == "PNG":
        save_kwargs["optimize"] = True
        save_kwargs["compress_level"] = 9

    if normalized == "JPEG":
        image = ensure_rgb(image)
    image.save(target_path, **save_kwargs)
    return str(target_path)


def zip_output_files(source_dir: Path, target_path: Path, pattern: str = "*") -> str:
    paths = sorted(path for path in source_dir.glob(pattern) if path.is_file())
    if not paths:
        raise AppException(message="没有可打包的文件", code=5002, status_code=500)
    with zipfile.ZipFile(target_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, arcname=path.name)
    return str(target_path)


def extract_zip_to_dir(input_path: str | Path, output_dir: str | Path) -> list[Path]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    try:
        with zipfile.ZipFile(input_path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                if member.filename.startswith("__MACOSX/"):
                    continue
                name = Path(member.filename).name
                if not name:
                    continue
                target = target_dir / name
                with archive.open(member) as src, target.open("wb") as dst:
                    dst.write(src.read())
                extracted.append(target)
    except zipfile.BadZipFile as exc:
        raise AppException(message="上传的压缩包无效", code=4002, status_code=400) from exc
    return extracted


def list_image_files(paths: list[Path]) -> list[Path]:
    return [path for path in paths if path.suffix.lower().lstrip(".") in IMAGE_SUFFIXES]


def parse_hex_color(value: str, default: str = "#ffffff") -> tuple[int, int, int]:
    try:
        return ImageColor.getrgb((value or default).strip())
    except ValueError as exc:
        raise AppException(message="颜色值格式无效", code=4001, status_code=400) from exc


def rgba_with_opacity(color: tuple[int, int, int], opacity_percent: int) -> tuple[int, int, int, int]:
    alpha = max(0, min(int(opacity_percent), 100)) * 255 // 100
    return color[0], color[1], color[2], alpha


def load_font(font_size: int) -> ImageFont.ImageFont:
    candidates = [
        # Linux CJK fonts used by the production server and common distributions.
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/opentype/source-han-sans/SourceHanSansCN-Regular.otf",
        "/usr/share/fonts/opentype/source-han-serif/SourceHanSerifCN-Regular.otf",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        "/usr/share/fonts/truetype/arphic/ukai.ttc",
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
        "/usr/share/fonts/opentype/unifont/unifont.otf",
        # macOS CJK fonts for local development.
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        # Windows CJK fonts for contributors running the app locally.
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        # Last resort: good Latin coverage, but not enough for Chinese.
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=font_size)
            except Exception:
                continue
    return ImageFont.load_default()


def resolve_position(
    base_size: tuple[int, int],
    mark_size: tuple[int, int],
    position: str = "bottom_right",
    padding: int = 16,
) -> tuple[int, int]:
    base_width, base_height = base_size
    mark_width, mark_height = mark_size
    horizontal = {
        "left": padding,
        "center": (base_width - mark_width) // 2,
        "right": max(padding, base_width - mark_width - padding),
    }
    vertical = {
        "top": padding,
        "middle": (base_height - mark_height) // 2,
        "bottom": max(padding, base_height - mark_height - padding),
    }
    mapping = {
        "top_left": (horizontal["left"], vertical["top"]),
        "top_center": (horizontal["center"], vertical["top"]),
        "top_right": (horizontal["right"], vertical["top"]),
        "center_left": (horizontal["left"], vertical["middle"]),
        "center": (horizontal["center"], vertical["middle"]),
        "center_right": (horizontal["right"], vertical["middle"]),
        "bottom_left": (horizontal["left"], vertical["bottom"]),
        "bottom_center": (horizontal["center"], vertical["bottom"]),
        "bottom_right": (horizontal["right"], vertical["bottom"]),
    }
    if position not in mapping:
        raise AppException(message="不支持的位置选项", code=4001, status_code=400)
    return mapping[position]


def draw_text_overlay(
    image: Image.Image,
    text: str,
    position: str,
    font_size: int,
    color: str,
    opacity: int,
) -> Image.Image:
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x, y = resolve_position(base.size, (width, height), position=position)
    draw.text((x, y), text, font=font, fill=rgba_with_opacity(parse_hex_color(color), opacity))
    return Image.alpha_composite(base, overlay)


def extract_office_media(input_path: str | Path, output_dir: str | Path, media_prefix: str, archive_name: str) -> str:
    output_root = Path(output_dir)
    media_dir = output_root / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    found = 0
    try:
        with zipfile.ZipFile(input_path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                if not member.filename.startswith(media_prefix):
                    continue
                name = Path(member.filename).name
                if not name:
                    continue
                found += 1
                target = media_dir / name
                with archive.open(member) as src, target.open("wb") as dst:
                    dst.write(src.read())
    except zipfile.BadZipFile as exc:
        raise AppException(message="上传的办公文档格式无效", code=4002, status_code=400) from exc

    if found == 0:
        raise AppException(message="文档中未找到图片资源", code=4002, status_code=400)

    return zip_output_files(media_dir, output_root / archive_name)


def image_to_bytes(image: Image.Image, output_format: str = "PNG") -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format=output_format)
    return buffer.getvalue()
