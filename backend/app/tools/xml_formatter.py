import xml.etree.ElementTree as ET

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "xml-formatter",
    "name": "XML 格式化/压缩",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def _strip_whitespace(element: ET.Element) -> None:
    if element.text:
        element.text = element.text.strip()
    if element.tail:
        element.tail = element.tail.strip()
    for child in list(element):
        _strip_whitespace(child)


def run(text: str, action: str = "format", **_: dict) -> str:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise AppException(message=f"XML 格式无效：{exc}", code=4001, status_code=400) from exc

    if action == "format":
        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode")
    if action == "minify":
        _strip_whitespace(root)
        return ET.tostring(root, encoding="unicode", method="xml")
    raise AppException(message="操作方式无效", code=4001, status_code=400)
