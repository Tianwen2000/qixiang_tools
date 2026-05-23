from datetime import datetime

from croniter import croniter

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "crontab-next-run",
    "name": "Crontab 执行时间计算",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, count: int = 5, **_: dict) -> str:
    expression = text.strip()
    if not expression:
        raise AppException(message="请输入 Cron 表达式", code=4001, status_code=400)

    count = int(count)
    if count not in {5, 10}:
        raise AppException(message="输出条数必须是 5 或 10", code=4001, status_code=400)

    now = datetime.now().replace(microsecond=0)
    try:
        iterator = croniter(expression, now)
    except Exception as exc:
        raise AppException(message=f"Cron 表达式无效：{exc}", code=4001, status_code=400) from exc

    lines = [f"当前时间: {now.isoformat(sep=' ')}", "未来执行时间:"]
    for index in range(count):
        next_time = iterator.get_next(datetime).replace(microsecond=0)
        lines.append(f"{index + 1}. {next_time.isoformat(sep=' ')}")
    return "\n".join(lines)
