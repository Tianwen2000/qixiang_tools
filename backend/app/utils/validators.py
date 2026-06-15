from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import AppException


IMAGE_TOOL_SLUGS = {
    "image-to-base64",
    "image-grid-splitter",
    "image-compressor",
    "image-cropper",
    "image-filter-processor",
    "image-watermarker",
    "image-format-converter",
    "image-color-analyzer",
    "image-color-picker",
    "image-exif-reader",
    "image-text-recognizer",
    "image-adjuster",
    "gif-splitter",
    "gif-scaler",
    "qr-code-decoder",
    "favicon-generator",
    "rounded-corner-image",
    "id-photo-cropper",
    "flag-avatar-generator",
    "image-upscaler",
    "image-background-remover",
    "image-resizer",
}
IMAGE_COMPRESSOR_EXTRA_SUFFIXES = {"heic", "heif"}
ZIP_IMAGE_TOOL_SLUGS = {
    "image-merger",
    "gif-maker",
    "gif-merger",
}
OFFICE_EXTRACT_TOOL_SUFFIXES = {
    "word-image-extractor": {"docx"},
    "excel-image-extractor": {"xlsx"},
    "ppt-image-extractor": {"pptx"},
}
DOCUMENT_TOOL_SUFFIXES = {
    "word-pdf-converter": {"docx", "pdf"},
    "pdf-jpg-converter": {"pdf", "jpg", "jpeg", "png", "webp", "bmp"},
    "pdf-epub-converter": {"pdf", "epub"},
    "pdf-txt-converter": {"pdf", "txt"},
    "pdf-html-converter": {"pdf", "html", "htm"},
    "word-txt-converter": {"docx", "txt"},
    "txt-epub-converter": {"txt", "epub"},
    "word-epub-converter": {"docx", "epub"},
    "word-html-converter": {"docx", "html", "htm"},
    "txt-html-converter": {"txt", "html", "htm"},
    "excel-csv-converter": {"xlsx", "csv"},
    "excel-txt-converter": {"xlsx", "txt"},
    "csv-txt-converter": {"csv", "txt"},
    "excel-html-converter": {"xlsx", "html", "htm"},
    "csv-html-converter": {"csv", "html", "htm"},
    "excel-pdf-converter": {"xlsx", "pdf"},
    "csv-pdf-converter": {"csv", "pdf"},
    "excel-word-converter": {"xlsx", "docx"},
    "csv-word-converter": {"csv", "docx"},
    "excel-epub-converter": {"xlsx", "epub"},
    "csv-epub-converter": {"csv", "epub"},
    "ppt-txt-converter": {"pptx", "txt"},
    "ppt-html-converter": {"pptx", "html", "htm"},
    "ppt-word-converter": {"pptx", "docx"},
    "ppt-pdf-converter": {"pptx", "pdf"},
    "ppt-epub-converter": {"pptx", "epub"},
    "json-xlsx-converter": {"json", "xlsx"},
    "docx-to-pdf": {"docx"},
    "pdf-to-word": {"pdf"},
    "pdf-to-jpg": {"pdf"},
    "jpg-to-pdf": {"jpg", "jpeg", "png", "webp", "bmp"},
    "pdf-to-epub": {"pdf"},
    "epub-to-pdf": {"epub"},
    "heic-to-pdf": {"heic", "heif"},
    "pdf-to-txt": {"pdf"},
    "word-to-txt": {"docx"},
    "txt-to-word": {"txt"},
    "txt-to-pdf": {"txt"},
    "txt-to-epub": {"txt"},
    "word-to-epub": {"docx"},
    "epub-to-word": {"epub"},
    "epub-to-txt": {"epub"},
    "word-to-html": {"docx"},
    "pdf-to-html": {"pdf"},
    "txt-to-html": {"txt"},
    "excel-to-csv": {"xlsx"},
    "csv-to-excel": {"csv"},
    "excel-to-html": {"xlsx"},
    "csv-to-html": {"csv"},
    "ppt-to-txt": {"pptx"},
    "ppt-to-html": {"pptx"},
    "ppt-to-word": {"pptx"},
    "ppt-to-pdf": {"pptx"},
    "excel-to-txt": {"xlsx"},
    "excel-to-pdf": {"xlsx"},
    "csv-to-txt": {"csv"},
    "csv-to-pdf": {"csv"},
    "excel-to-word": {"xlsx"},
    "csv-to-word": {"csv"},
    "excel-to-epub": {"xlsx"},
    "csv-to-epub": {"csv"},
    "ppt-to-epub": {"pptx"},
}
MEDIA_TOOL_SUFFIXES = {
    "mp3-flac-converter": {"mp3", "flac"},
    "wav-mp3-converter": {"wav", "mp3"},
    "mov-mp4-converter": {"mov", "mp4"},
    "mp3-mp4-converter": {"mp3", "mp4"},
    "gif-mp4-converter": {"gif", "mp4"},
}
GIF_IMAGE_TOOL_SUFFIXES = {
    "gif-png-converter": {"gif", "png"},
    "gif-jpg-converter": {"gif", "jpg", "jpeg"},
}
SVG_IMAGE_TOOL_SUFFIXES = {
    "jpg-svg-converter": {"jpg", "jpeg", "svg"},
    "png-svg-converter": {"png", "svg"},
    "gif-svg-converter": {"gif", "svg"},
}


def validate_tool_supports_mode(input_mode: str, allowed: set[str]) -> None:
    if input_mode not in allowed:
        raise AppException(message="该工具不支持当前请求方式", code=4001, status_code=400)


def validate_upload_for_tool(file: UploadFile, tool_slug: str) -> None:
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower().lstrip(".")
    content_type = (file.content_type or "").lower()

    if tool_slug in IMAGE_TOOL_SLUGS:
        allowed_suffixes = set(settings.allowed_image_types)
        if tool_slug == "image-compressor":
            allowed_suffixes.update(IMAGE_COMPRESSOR_EXTRA_SUFFIXES)

        if suffix not in allowed_suffixes:
            raise AppException(message="不支持的图片类型", code=4002, status_code=400)

        content_type_allowed = not content_type or content_type.startswith("image/")
        if (
            tool_slug == "image-compressor"
            and suffix in IMAGE_COMPRESSOR_EXTRA_SUFFIXES
            and content_type in {"application/octet-stream", "binary/octet-stream"}
        ):
            content_type_allowed = True

        if not content_type_allowed:
            raise AppException(message="无效的图片文件", code=4002, status_code=400)
    elif tool_slug in ZIP_IMAGE_TOOL_SLUGS:
        if suffix != "zip":
            raise AppException(message="请上传 zip 压缩包", code=4002, status_code=400)
    elif tool_slug == "xlsx-to-json":
        if suffix != "xlsx":
            raise AppException(message="只支持 .xlsx 文件", code=4002, status_code=400)
    elif tool_slug == "sqlite-viewer":
        if suffix not in {"db", "sqlite", "sqlite3"}:
            raise AppException(message="只支持 SQLite 数据库文件", code=4002, status_code=400)
    elif tool_slug in OFFICE_EXTRACT_TOOL_SUFFIXES:
        if suffix not in OFFICE_EXTRACT_TOOL_SUFFIXES[tool_slug]:
            raise AppException(message="上传文件类型不正确", code=4002, status_code=400)
    elif tool_slug in DOCUMENT_TOOL_SUFFIXES:
        if suffix not in DOCUMENT_TOOL_SUFFIXES[tool_slug]:
            raise AppException(message="上传文件类型不正确", code=4002, status_code=400)
    elif tool_slug in MEDIA_TOOL_SUFFIXES:
        if suffix not in MEDIA_TOOL_SUFFIXES[tool_slug]:
            raise AppException(message="上传文件类型不正确", code=4002, status_code=400)
    elif tool_slug in GIF_IMAGE_TOOL_SUFFIXES:
        if suffix not in GIF_IMAGE_TOOL_SUFFIXES[tool_slug]:
            raise AppException(message="上传文件类型不正确", code=4002, status_code=400)
    elif tool_slug in SVG_IMAGE_TOOL_SUFFIXES:
        if suffix not in SVG_IMAGE_TOOL_SUFFIXES[tool_slug]:
            raise AppException(message="上传文件类型不正确", code=4002, status_code=400)
        if content_type and not content_type.startswith("image/"):
            raise AppException(message="无效的图片文件", code=4002, status_code=400)
