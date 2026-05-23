from app.utils.codegen_utils import ensure_object_schema, load_json_value, pascal_case


TOOL_META = {
    "slug": "json-to-csharp",
    "name": "JSON 转 C# 实体类",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


class CSharpGenerator:
    def __init__(self) -> None:
        self.classes: dict[str, list[tuple[str, str]]] = {}
        self.order: list[str] = []
        self.needs_list = False

    def infer_type(self, value, type_name: str) -> str:
        if isinstance(value, dict):
            class_name = pascal_case(type_name)
            if class_name not in self.classes:
                self.classes[class_name] = []
                self.order.append(class_name)
                for key, item in value.items():
                    property_name = pascal_case(key, default="Field")
                    nested_type = self.infer_type(item, f"{class_name}{property_name}")
                    self.classes[class_name].append((property_name, nested_type))
            return class_name
        if isinstance(value, list):
            self.needs_list = True
            if not value:
                return "List<object>"
            item_type = self.infer_type(value[0], f"{type_name}Item")
            return f"List<{item_type}>"
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "long"
        if isinstance(value, float):
            return "double"
        if value is None:
            return "object"
        return "string"

    def _default_value(self, type_name: str) -> str:
        if type_name == "string":
            return ' = "";'
        if type_name.startswith("List<"):
            return " = new();"
        return ""

    def render(self, schema: dict, root_name: str) -> str:
        root_class = pascal_case(root_name)
        self.infer_type(schema, root_class)
        lines = []
        if self.needs_list:
            lines.append("using System.Collections.Generic;")
            lines.append("")
        for index, class_name in enumerate(self.order):
            lines.append(f"public class {class_name}")
            lines.append("{")
            for property_name, type_name in self.classes[class_name]:
                lines.append(f"    public {type_name} {property_name} {{ get; set; }}{self._default_value(type_name)}")
            lines.append("}")
            if index != len(self.order) - 1:
                lines.append("")
        return "\n".join(lines)


def run(text: str, root_name: str = "Root", **_: dict) -> str:
    parsed = load_json_value(text)
    schema = ensure_object_schema(parsed)
    generator = CSharpGenerator()
    return generator.render(schema, root_name or "Root")
