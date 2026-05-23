from app.utils.codegen_utils import ensure_object_schema, load_json_value, snake_case


TOOL_META = {
    "slug": "json-to-sql",
    "name": "JSON 转 SQL",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def _column_type(value) -> str:
    if isinstance(value, bool):
        return "BOOLEAN"
    if isinstance(value, int):
        return "BIGINT"
    if isinstance(value, float):
        return "DECIMAL(18,6)"
    if isinstance(value, (dict, list)):
        return "JSON"
    return "TEXT"


def run(text: str, table_name: str = "sample_table", **_: dict) -> str:
    parsed = load_json_value(text)
    schema = ensure_object_schema(parsed)
    name = snake_case(table_name or "sample_table", default="sample_table")

    lines = [f"CREATE TABLE {name} ("]
    if "id" not in schema:
        lines.append("  id BIGINT PRIMARY KEY AUTO_INCREMENT,")

    items = list(schema.items())
    for index, (key, value) in enumerate(items):
        column_name = snake_case(key)
        suffix = "," if index != len(items) - 1 else ""
        if key == "id":
            lines.append(f"  {column_name} {_column_type(value)} PRIMARY KEY{suffix}")
        else:
            lines.append(f"  {column_name} {_column_type(value)}{suffix}")

    lines.append(");")
    return "\n".join(lines)
