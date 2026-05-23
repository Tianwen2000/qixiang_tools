import json
import sqlite3
from pathlib import Path

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "sqlite-viewer",
    "name": "SQLite 查看器",
    "category": "dev",
    "input_mode": "file",
    "result_type": "text",
}


def run(input_path: str, preview_limit: int = 20, **_: dict) -> str:
    path = Path(input_path)
    try:
        preview_limit = int(preview_limit)
    except (TypeError, ValueError) as exc:
        raise AppException(message="preview_limit 必须是整数", code=4001, status_code=400) from exc

    preview_limit = max(1, min(preview_limit, 50))

    try:
        connection = sqlite3.connect(path)
    except sqlite3.Error as exc:
        raise AppException(message=f"无法打开 SQLite 文件: {exc}", code=4002, status_code=400) from exc

    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        table_rows = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        tables = [row["name"] for row in table_rows]

        payload = {
            "table_count": len(tables),
            "tables": [],
        }

        for table_name in tables:
            count_row = cursor.execute(f'SELECT COUNT(*) AS count FROM "{table_name}"').fetchone()
            sample_rows = cursor.execute(f'SELECT * FROM "{table_name}" LIMIT ?', (preview_limit,)).fetchall()
            payload["tables"].append(
                {
                    "name": table_name,
                    "row_count": count_row["count"] if count_row else 0,
                    "preview": [dict(row) for row in sample_rows],
                }
            )
    except sqlite3.Error as exc:
        raise AppException(message=f"读取 SQLite 数据失败: {exc}", code=4002, status_code=400) from exc
    finally:
        connection.close()

    return json.dumps(payload, ensure_ascii=False, indent=2)
