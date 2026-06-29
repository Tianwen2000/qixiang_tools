TOOL_META = {
    "slug": "npm-node-vite-command-search",
    "name": "npm、node等包管理工具命令集合",
    "category": "ops",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地命令大全，请在页面中直接查看。"
