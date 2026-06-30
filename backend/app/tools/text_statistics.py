"""文件说明：实现「字数统计」工具的后端逻辑。"""

TOOL_META = {
    "slug": "text-statistics",
    "name": "字数统计",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, **_: dict) -> str:
    lines = text.splitlines()
    words = [word for word in text.split() if word]
    chinese_chars = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    result_lines = [
        f"总字符数：{len(text)}",
        f"非空白字符数：{len(''.join(char for char in text if not char.isspace()))}",
        f"汉字数量：{chinese_chars}",
        f"单词数量：{len(words)}",
        f"总行数：{len(lines)}",
        f"非空行数：{len([line for line in lines if line.strip()])}",
        f"UTF-8 字节数：{len(text.encode('utf-8'))}",
    ]
    return "\n".join(result_lines)
