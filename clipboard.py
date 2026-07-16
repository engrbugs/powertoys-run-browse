import pyperclip


def copy_to_clipboard(string_to_copy: str) -> None:
    pyperclip.copy(string_to_copy)
