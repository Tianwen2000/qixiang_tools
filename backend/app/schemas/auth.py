"""文件说明：定义 auth 相关接口的数据结构。"""

"""登录/注册请求体。

只做长度上限保护，真正的格式校验放在 ``auth_service`` 里，
这样错误能走统一的 ``AppException`` 响应壳（{code,message,data}），
前端可以直接拿到具体中文提示，而不是 FastAPI 默认的 422 结构。
"""

from pydantic import BaseModel, Field


class AuthInput(BaseModel):
    account: str = Field(default="", max_length=64)
    password: str = Field(default="", max_length=128)
