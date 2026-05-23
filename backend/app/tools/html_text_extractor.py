from html.parser import HTMLParser

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "html-text-extractor",
    "name": "HTML 提取文字",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []
        self._ignored_tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        _ = attrs
        if tag in {"script", "style"}:
            self._ignored_tags.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if self._ignored_tags and self._ignored_tags[-1] == tag:
            self._ignored_tags.pop()

    def handle_data(self, data: str) -> None:
        if self._ignored_tags:
            return
        stripped = data.strip()
        if stripped:
            self.chunks.append(stripped)


def run(text: str, join_mode: str = "multiline", **_: dict) -> str:
    parser = _TextExtractor()
    parser.feed(text)
    parser.close()

    if join_mode == "single_line":
        return " ".join(parser.chunks)
    if join_mode == "multiline":
        return "\n".join(parser.chunks)
    raise AppException(message="拼接模式必须是 single_line 或 multiline", code=4001, status_code=400)
