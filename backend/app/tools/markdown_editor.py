"""文件说明：实现「Markdown 编辑器」工具的后端逻辑。"""

import markdown


TOOL_META = {
    "slug": "markdown-editor",
    "name": "Markdown 编辑器",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, **_: dict) -> str:
    return markdown.markdown(
        text,
        extensions=[
            "extra",
            "fenced_code",
            "tables",
            "sane_lists",
            "toc",
        ],
        output_format="html5",
    )
