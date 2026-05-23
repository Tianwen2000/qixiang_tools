from collections import Counter


TOOL_META = {
    "slug": "duplicate-line-counter",
    "name": "重复行统计",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, include_single: bool = False, sort_by: str = "count_desc", **_: dict) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    counter = Counter(lines)
    items = [(line, count) for line, count in counter.items() if include_single or count > 1]

    if sort_by == "count_desc":
        items.sort(key=lambda item: (-item[1], item[0]))
    elif sort_by == "count_asc":
        items.sort(key=lambda item: (item[1], item[0]))
    elif sort_by == "text_asc":
        items.sort(key=lambda item: item[0])
    else:
        items.sort(key=lambda item: item[0], reverse=True)

    if not items:
        return "未发现重复行"
    return "\n".join(f"{line}  x {count}" for line, count in items)
