"""文件说明：按 tools.json 动态导入工具模块并执行对应处理函数。"""

from functools import lru_cache
from importlib import import_module
from types import ModuleType

from app.core.exceptions import AppException
from app.services.tool_loader import get_tool_detail


@lru_cache
def get_tool_module(slug: str) -> ModuleType:
    tool_meta = get_tool_detail(slug)
    try:
        module = import_module(f"app.tools.{tool_meta.module}")
    except ImportError as exc:
        raise AppException(message=f"工具模块加载失败：{tool_meta.module}", code=5001, status_code=500) from exc

    if not hasattr(module, "run"):
        raise AppException(message=f"工具模块缺少 run() 方法：{tool_meta.module}", code=5001, status_code=500)

    return module
