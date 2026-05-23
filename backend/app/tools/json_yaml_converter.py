import json

import yaml

from app.core.exceptions import AppException
from app.utils.codegen_utils import load_json_value


TOOL_META = {
    "slug": "json-yaml-converter",
    "name": "JSON/YAML 互转",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def _json_to_yaml(text: str) -> str:
    parsed = load_json_value(text)
    return yaml.safe_dump(parsed, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _yaml_to_json(text: str) -> str:
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise AppException(message=f"YAML 格式无效：{exc}", code=4001, status_code=400) from exc
    return json.dumps(parsed, ensure_ascii=False, indent=2)


def run(text: str, action: str = "json_to_yaml", **_: dict) -> str:
    if action == "json_to_yaml":
        return _json_to_yaml(text)
    if action == "yaml_to_json":
        return _yaml_to_json(text)
    raise AppException(message="操作方式无效", code=4001, status_code=400)
