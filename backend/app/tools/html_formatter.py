import re
from html.parser import HTMLParser


from app.core.exceptions import AppException


TOOL_META = {
    "slug": "html-formatter",
    "name": "HTML 格式化/压缩",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class _HTMLFormatter(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.level = 0
        self.lines: list[str] = []

    def _append(self, value: str) -> None:
        self.lines.append(f"{'  ' * self.level}{value}")

    def handle_decl(self, decl: str) -> None:
        self._append(f"<!{decl}>")

    def handle_comment(self, data: str) -> None:
        self._append(f"<!--{data}-->")

    def handle_starttag(self, tag: str, attrs) -> None:
        rendered_attrs = "".join(f' {name}="{value}"' if value is not None else f" {name}" for name, value in attrs)
        self._append(f"<{tag}{rendered_attrs}>")
        if tag.lower() not in VOID_TAGS:
            self.level += 1

    def handle_startendtag(self, tag: str, attrs) -> None:
        rendered_attrs = "".join(f' {name}="{value}"' if value is not None else f" {name}" for name, value in attrs)
        self._append(f"<{tag}{rendered_attrs} />")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() not in VOID_TAGS:
            self.level = max(self.level - 1, 0)
        self._append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        stripped = data.strip()
        if stripped:
            for line in stripped.splitlines():
                content = line.strip()
                if content:
                    self._append(content)


def _format_html(text: str) -> str:
    parser = _HTMLFormatter()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        raise AppException(message=f"HTML 格式无效：{exc}", code=4001, status_code=400) from exc
    return "\n".join(parser.lines)


def _minify_html(text: str) -> str:
    content = re.sub(r">\s+<", "><", text.strip())
    content = re.sub(r"\n+", "", content)
    return content


def run(text: str, action: str = "format", **_: dict) -> str:
    if action == "format":
        return _format_html(text)
    if action == "minify":
        return _minify_html(text)
    raise AppException(message="操作方式无效", code=4001, status_code=400)
