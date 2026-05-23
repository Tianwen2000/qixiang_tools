from app.utils.codegen_utils import ensure_object_schema, load_json_value, pascal_case


TOOL_META = {
    "slug": "json-to-golang",
    "name": "JSON 转 Golang 结构体",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


class GoGenerator:
    def __init__(self) -> None:
        self.structs: dict[str, list[tuple[str, str, str]]] = {}
        self.order: list[str] = []

    def infer_type(self, value, type_name: str) -> str:
        if isinstance(value, dict):
            struct_name = pascal_case(type_name)
            if struct_name not in self.structs:
                self.structs[struct_name] = []
                self.order.append(struct_name)
                for key, item in value.items():
                    field_name = pascal_case(key, default="Field")
                    nested_type = self.infer_type(item, f"{struct_name}{field_name}")
                    self.structs[struct_name].append((key, field_name, nested_type))
            return struct_name
        if isinstance(value, list):
            if not value:
                return "[]any"
            item_type = self.infer_type(value[0], f"{type_name}Item")
            return f"[]{item_type}"
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int64"
        if isinstance(value, float):
            return "float64"
        if value is None:
            return "any"
        return "string"

    def render(self, schema: dict, root_name: str) -> str:
        root_struct = pascal_case(root_name)
        self.infer_type(schema, root_struct)
        blocks = []
        for struct_name in self.order:
            lines = [f"type {struct_name} struct {{"]
            for json_key, field_name, field_type in self.structs[struct_name]:
                lines.append(f'    {field_name} {field_type} `json:"{json_key}"`')
            lines.append("}")
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks)


def run(text: str, root_name: str = "Root", **_: dict) -> str:
    parsed = load_json_value(text)
    schema = ensure_object_schema(parsed)
    generator = GoGenerator()
    return generator.render(schema, root_name or "Root")
