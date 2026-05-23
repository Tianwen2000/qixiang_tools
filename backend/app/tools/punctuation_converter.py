from app.core.exceptions import AppException


TOOL_META = {
    "slug": "punctuation-converter",
    "name": "中英文标点转换",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


CN_TO_EN = str.maketrans(
    {
        "，": ",",
        "。": ".",
        "：": ":",
        "；": ";",
        "！": "!",
        "？": "?",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "《": "<",
        "》": ">",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "、": ",",
        "￥": "$",
    }
)
EN_TO_CN = str.maketrans(
    {
        ",": "，",
        ".": "。",
        ":": "：",
        ";": "；",
        "!": "！",
        "?": "？",
        "(": "（",
        ")": "）",
        "[": "【",
        "]": "】",
        "<": "《",
        ">": "》",
        '"': "“",
        "'": "‘",
        "$": "￥",
    }
)


def run(text: str, action: str = "cn_to_en", **_: dict) -> str:
    if action == "cn_to_en":
        return text.translate(CN_TO_EN)
    if action == "en_to_cn":
        return text.translate(EN_TO_CN)
    raise AppException(message="不支持的标点转换方式", code=4001, status_code=400)
