n = "\n"
w = " "

bold = lambda x: f"<b>{x}:</b> "
bold_ul = lambda x: f"<b>--{x}:</b>-- "

mono = lambda x: f"`{x}`{n}"


def section(
        title: str,
        body: dict,
        indent: int = 2,
        underline: bool = False,
) -> str:
    text = (bold_ul(title) + n) if underline else bold(title) + n

    for key, value in body.items():
        text += (
                indent * w
                + bold(key)
                + ((value[0] + n) if isinstance(value, list) else mono(value))
        )
    return text
