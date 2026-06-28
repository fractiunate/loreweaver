import re


def heading_path_at(text: str, start_offset: int, end_offset: int) -> str:
    stack: list[str] = []
    heading_regex = r"^(#{1,6})\s+(.+?)\s*$"

    for line in text[:start_offset].splitlines():
        match = re.match(heading_regex, line)
        if not match:
            continue

        level = len(match.group(1))
        title = match.group(2).strip().strip("#").strip()

        stack = stack[: level - 1]
        stack.append(title)

    if not stack:
        for line in text[start_offset:end_offset].splitlines():
            match = re.match(heading_regex, line)
            if not match:
                continue

            stack.append(match.group(2).strip())
            break

    return " > ".join(stack)
