from app.core.exceptions import AppException


TOOL_META = {
    "slug": "directory-tree-generator",
    "name": "目录树生成",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def _insert_path(tree: dict, raw_path: str) -> None:
    cleaned = raw_path.strip().replace("\\", "/").strip("/")
    if not cleaned:
        return
    node = tree
    for part in [item for item in cleaned.split("/") if item]:
        node = node.setdefault(part, {})


def _render(tree: dict, prefix: str = "") -> list[str]:
    lines: list[str] = []
    items = list(tree.items())
    for index, (name, children) in enumerate(items):
        connector = "└── " if index == len(items) - 1 else "├── "
        lines.append(f"{prefix}{connector}{name}")
        child_prefix = f"{prefix}{'    ' if index == len(items) - 1 else '│   '}"
        lines.extend(_render(children, child_prefix))
    return lines


def run(text: str, **_: dict) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise AppException(message="请输入路径列表", code=4001, status_code=400)

    tree: dict = {}
    for line in lines:
        _insert_path(tree, line)
    return "\n".join(_render(tree))
