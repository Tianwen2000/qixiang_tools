"""文件说明：实现「响应式布局检测」工具的后端逻辑。"""

TOOL_META = {
    "slug": "responsive-layout-checker",
    "name": "响应式布局检测",
    "category": "dev",
    "input_mode": "form",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "请在前端页面中使用该工具，当前视口尺寸和断点状态会在本地实时展示。"
