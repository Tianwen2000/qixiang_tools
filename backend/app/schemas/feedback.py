"""文件说明：定义 feedback 相关接口的数据结构。"""

"""反馈提交请求体。

仅对主文本 ``content`` 设一个宽松上限做防滥用保护；其余元信息字段不在此设限，
统一交给 ``feedback_service`` 按数据库列长度截断（截断而非拒绝），错误走 ``AppException`` 响应壳。
"""

from pydantic import BaseModel, Field


class FeedbackInput(BaseModel):
    content: str = Field(default="", max_length=20000)
    feedbackType: str = Field(default="")
    toolSlug: str = Field(default="")
    toolName: str = Field(default="")
    toolUrl: str = Field(default="")
    contactType: str = Field(default="")
    contactValue: str = Field(default="")
    submittedPage: str = Field(default="")
    userAgent: str = Field(default="")
    deviceId: str = Field(default="")
