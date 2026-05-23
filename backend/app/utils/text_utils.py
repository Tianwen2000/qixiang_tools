from collections.abc import Iterable


def deduplicate_lines(text: str, keep_empty: bool = False) -> str:
    seen: set[str] = set()
    result: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line if keep_empty else raw_line.strip()
        if not line and not keep_empty:
            continue
        if line not in seen:
            seen.add(line)
            result.append(line)
    return "\n".join(result)


def unique_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def split_non_empty_lines(text: str, strip: bool = True) -> list[str]:
    result: list[str] = []
    for line in text.splitlines():
        value = line.strip() if strip else line
        if value:
            result.append(value)
    return result
