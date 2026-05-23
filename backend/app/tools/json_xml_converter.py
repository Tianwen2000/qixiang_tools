import json
import re
import xml.etree.ElementTree as ET

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "json-xml-converter",
    "name": "JSON/XML 互转",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


_XML_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


def _safe_tag(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]", "_", str(name).strip())
    if not cleaned:
        return "item"
    if _XML_NAME_RE.match(cleaned):
        return cleaned
    return f"n_{cleaned}"


def _to_xml_element(tag: str, value):
    element = ET.Element(_safe_tag(tag))
    if isinstance(value, dict):
        for key, item in value.items():
            element.append(_to_xml_element(str(key), item))
    elif isinstance(value, list):
        for item in value:
            element.append(_to_xml_element("item", item))
    elif value is None:
        element.set("isNull", "true")
    elif isinstance(value, bool):
        element.set("type", "bool")
        element.text = "true" if value else "false"
    elif isinstance(value, (int, float)):
        element.set("type", "number")
        element.text = str(value)
    else:
        element.text = str(value)
    return element


def _parse_text_value(text: str, type_hint: str):
    if type_hint == "bool":
        return text.lower() == "true"
    if type_hint == "number":
        if any(char in text.lower() for char in [".", "e"]):
            return float(text)
        return int(text)
    return text


def _from_xml_element(element: ET.Element):
    if element.get("isNull") == "true":
        return None

    children = list(element)
    if not children:
        text = (element.text or "").strip()
        return _parse_text_value(text, element.get("type", ""))

    grouped: dict[str, list] = {}
    for child in children:
        grouped.setdefault(child.tag, []).append(_from_xml_element(child))

    if set(grouped) == {"item"}:
        return grouped["item"]

    result = {}
    for key, values in grouped.items():
        result[key] = values[0] if len(values) == 1 else values
    return result


def _json_to_xml(text: str) -> str:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AppException(message=f"JSON 格式无效：{exc.msg}", code=4001, status_code=400) from exc

    root = _to_xml_element("root", parsed)
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode")


def _xml_to_json(text: str) -> str:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise AppException(message=f"XML 格式无效：{exc}", code=4001, status_code=400) from exc
    return json.dumps(_from_xml_element(root), ensure_ascii=False, indent=2)


def run(text: str, action: str = "json_to_xml", **_: dict) -> str:
    if action == "json_to_xml":
        return _json_to_xml(text)
    if action == "xml_to_json":
        return _xml_to_json(text)
    raise AppException(message="操作方式无效", code=4001, status_code=400)
