from app.utils.codegen_utils import load_json_value, pascal_case, safe_ts_property_name


TOOL_META = {
    "slug": "json-to-typescript",
    "name": "JSON 转 TypeScript",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


class TypeScriptGenerator:
    def __init__(self) -> None:
        self.definitions: dict[str, list[tuple[str, str]]] = {}
        self.order: list[str] = []

    def infer_type(self, value, type_name: str) -> str:
        if isinstance(value, dict):
            interface_name = pascal_case(type_name)
            if interface_name not in self.definitions:
                self.definitions[interface_name] = []
                self.order.append(interface_name)
                for key, item in value.items():
                    nested_type = self.infer_type(item, f"{interface_name}{pascal_case(key)}")
                    self.definitions[interface_name].append((key, nested_type))
            return interface_name
        if isinstance(value, list):
            if not value:
                return "unknown[]"
            item_types = []
            for index, item in enumerate(value):
                inferred = self.infer_type(item, f"{type_name}Item{index + 1}")
                if inferred not in item_types:
                    item_types.append(inferred)
            item_type = item_types[0] if len(item_types) == 1 else " | ".join(item_types)
            if " | " in item_type:
                item_type = f"({item_type})"
            return f"{item_type}[]"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, (int, float)):
            return "number"
        if value is None:
            return "null"
        return "string"

    def render(self, root_value, root_name: str) -> str:
        root_type = self.infer_type(root_value, root_name)
        if root_type in self.definitions:
            blocks = []
            for name in self.order:
                lines = [f"export interface {name} {{"]
                for key, type_name in self.definitions[name]:
                    lines.append(f"  {safe_ts_property_name(key)}: {type_name};")
                lines.append("}")
                blocks.append("\n".join(lines))
            return "\n\n".join(blocks)
        return f"export type {pascal_case(root_name)} = {root_type};"


def run(text: str, root_name: str = "Root", **_: dict) -> str:
    parsed = load_json_value(text)
    generator = TypeScriptGenerator()
    return generator.render(parsed, root_name or "Root")
