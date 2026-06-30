"""文件说明：实现「大数据 Hadoop 生态命令」工具的后端逻辑。"""

TOOL_META = {
    "slug": "hadoop-ecosystem-command-search",
    "name": "大数据 Hadoop 生态命令",
    "category": "ops",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地命令大全，请在页面中直接查看。"
