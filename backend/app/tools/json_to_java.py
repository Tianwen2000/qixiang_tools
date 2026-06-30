"""文件说明：实现「JSON 转 Java 实体类」工具的后端逻辑。"""

from app.utils.codegen_utils import camel_case, ensure_object_schema, load_json_value, pascal_case


TOOL_META = {
    "slug": "json-to-java",
    "name": "JSON 转 Java 实体类",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


class JavaGenerator:
    def __init__(self) -> None:
        self.classes: dict[str, list[tuple[str, str, str]]] = {}
        self.order: list[str] = []
        self.needs_list = False

    def infer_type(self, value, type_name: str) -> str:
        if isinstance(value, dict):
            class_name = pascal_case(type_name)
            if class_name not in self.classes:
                self.classes[class_name] = []
                self.order.append(class_name)
                for key, item in value.items():
                    field_name = camel_case(key)
                    nested_type = self.infer_type(item, f"{class_name}{pascal_case(key)}")
                    self.classes[class_name].append((key, field_name, nested_type))
            return class_name
        if isinstance(value, list):
            self.needs_list = True
            if not value:
                return "List<Object>"
            item_type = self.infer_type(value[0], f"{type_name}Item")
            return f"List<{item_type}>"
        if isinstance(value, bool):
            return "Boolean"
        if isinstance(value, int):
            return "Long"
        if isinstance(value, float):
            return "Double"
        if value is None:
            return "Object"
        return "String"

    def render(self, schema: dict, root_name: str) -> str:
        root_class = pascal_case(root_name)
        self.infer_type(schema, root_class)
        lines = []
        if self.needs_list:
            lines.append("import java.util.List;")
            lines.append("")
        for index, class_name in enumerate(self.order):
            lines.append(f"public class {class_name} {{")
            for original_key, field_name, type_name in self.classes[class_name]:
                if field_name != original_key:
                    lines.append(f"    // json key: {original_key}")
                lines.append(f"    public {type_name} {field_name};")
                lines.append("")
            if lines[-1] == "":
                lines.pop()
            lines.append("}")
            if index != len(self.order) - 1:
                lines.append("")
        return "\n".join(lines)


def run(text: str, root_name: str = "Root", **_: dict) -> str:
    parsed = load_json_value(text)
    schema = ensure_object_schema(parsed)
    generator = JavaGenerator()
    return generator.render(schema, root_name or "Root")
