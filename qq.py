#! /usr/bin/env python3
"""Launch web browsers and prompt helpers for PowerToys Run."""

from __future__ import annotations

import datetime
import time
import webbrowser

import clipboard as cp
import pyperclip
from dateutil.parser import parse

VERSION = "1.2.1"
DEFAULT_OPTION = "1"

SHORTCUTS = {
    "Define": ["https://www.google.com/search?q={words} define", "1", "q"],
    "Thesaurus": ["https://www.google.com/search?q={words} thesaurus", "2", "w"],
    "Youtube": ["https://www.youtube.com/results?search_query={words}", "3", "y"],
    "Reverse Dictionary": ["https://www.onelook.com/reverse-dictionary.shtml?s={words}", "4", "q"],
    "Google Pronunciation": ["https://www.google.com/search?q={words} pronunciation", "5", "p"],
    "Github": ["https://github.com/search?q={words}", "6", "g"],
    "stackoverflow": ["https://stackoverflow.com/search?q={words}", "7", "s"],
    "Calendar": ["https://calendar.google.com/calendar/u/0/r/day/{words}", "8"],
    "Reddit": ["https://www.reddit.com/", "R"],
    "Twitter": ["https://www.twitter.com/", "T"],
    "Ludwig": ["https://ludwig.guru/s/{words}", "9", "L"],
    "Bible": [
        "https://www.biblegateway.com/quicksearch/?quicksearch={words}&version=NIV",
        "B",
    ],
    "Chat-GPT": ["[chat_gpt]", "C"],
    "GrammarGPT": ["[GrammarGPT]", "C1", True],
}

CHATGPT = {
    "1": {
        "title": "Grammar Fix",
        "prompts": ["Please correct the grammar and punctuation from my dictation:\n(X)"],
    },
    "2": {
        "title": "Improve Paragraph",
        "prompts": ["Improve my paragraph"],
    },
    "3": {
        "title": "Make Powerful",
        "prompts": ["Make that powerful"],
    },
    "4": {
        "title": "Draft Email",
        "prompts": ["(X)\nCompose an email draft that addresses the above context. Here's the response points:"],
    },
    "5": {
        "title": "Summarize Simply",
        "prompts": ["Summarize this for a high school student:\n"],
    },
    "55": {
        "title": "Explain Like 5",
        "prompts": ["Explain that to me like I'm a five-year-old kid"],
    },
    "6": {
        "title": "Compare Things",
        "prompts": ["What is the difference between "],
    },
    "7": {
        "title": "Conversation Checkpoint",
        "prompts": [
            """
Act as a documentation archivist.

Consolidate our entire conversation into a single Markdown (.md) file for saving as a checkpoint.

**Requirements:**
1. **Title:** Start with a clear top-level title using `#` (e.g., `# Conversation Checkpoint: [Topic or Date]`).
2. **Structure:** Label each message using:
   - `## User`
   - `## Assistant`
3. **Integrity:** Preserve all original formatting exactly (code blocks, lists, LaTeX, tables, etc.).
4. **Separation:** Insert a horizontal rule (`---`) between each full exchange.
5. **Completeness:** Include the full conversation history without summarizing or omitting anything.
6. **Output Format:** Wrap the entire result inside a single Markdown code block for easy copy-paste.

Generate the complete `.md` file now.
          """
        ],
    },
}


def count_visible_shortcuts(shortcuts_dict: dict[str, list[object]]) -> int:
    visible_count = 0
    for value in shortcuts_dict.values():
        if value and value[-1] is not False:
            visible_count += 1
    return visible_count


def grammar_gpt(words: str) -> None:
    if not words:
        words = "1"

    if words in CHATGPT:
        text_in_clipboard = pyperclip.paste()
        prompt = CHATGPT[words]["prompts"][0]
        cp.copy_to_clipboard(prompt.replace("(X)", text_in_clipboard))
    else:
        print(f"Invalid option: {words}")


def GrammarGPT(words: str) -> None:
    """Keep the original callable name used by shortcut dispatch."""
    grammar_gpt(words)


def chat_gpt(words: str) -> None:
    if not words:
        print("ChatGPT prompts")
        for key, value in CHATGPT.items():
            print(f"{key:>2}  {value['title']}")
        print("pick number", end=":                        ")
        words = input().strip()

    if words in CHATGPT:
        text_in_clipboard = pyperclip.paste()
        prompts = CHATGPT[words]["prompts"]
        for phrase in prompts:
            cp.copy_to_clipboard(phrase.replace("(X)", text_in_clipboard))
            if len(prompts) != 1:
                time.sleep(1)


def open_main_website(link: str, append: str = "") -> None:
    main_website = link[: link.find("/", 9) + 1]
    webbrowser.open(main_website + append)
    raise SystemExit


def run_function(func_name: str, *args: str) -> None:
    globals()[func_name](*args)


def prompt_for_search_terms() -> str:
    print("What to search", end=":                        ")
    return input().strip() or "main"


def encode_hash_characters(words: str) -> str:
    return words.replace("#", "%23")


def resolve_calendar_words(words: str) -> str:
    while True:
        if words in {"", "main"}:
            main_website = SHORTCUTS["Calendar"][0][: SHORTCUTS["Calendar"][0].rfind("/")].replace(
                "day", "month"
            )
            webbrowser.open(main_website)
            raise SystemExit

        try:
            parsed_date = parse(words)
            return parsed_date.strftime("%Y/%#m/%#d")
        except (OverflowError, TypeError, ValueError):
            today = datetime.date.today()
            lowered = words.lower()
            if lowered in {"today", "now"}:
                return today.strftime("%Y/%#m/%#d")
            if lowered in {"yesterday", "yday"}:
                return (today - datetime.timedelta(days=1)).strftime("%Y/%#m/%#d")
            if lowered in {"tomorrow", "tom"}:
                return (today + datetime.timedelta(days=1)).strftime("%Y/%#m/%#d")

            print("Cannot read date")
            print("Please enter new date or press ENTER for month)", end=":    ")
            words = input().strip()


def browse(browse_choice: str, words: str) -> None:
    print(f"opening, {browse_choice}, {words}")
    normalized_choice = {browse_choice.lower(), browse_choice.upper()}

    for title, shortcut in SHORTCUTS.items():
        if not any(option in shortcut for option in normalized_choice):
            continue

        target = shortcut[0]
        if "{" in target:
            if title == "Calendar":
                words = resolve_calendar_words(words)
            else:
                words = encode_hash_characters(words)
                if not words:
                    words = prompt_for_search_terms()
        elif "[" in target:
            function_name = target.replace("[", "").replace("]", "")
            run_function(function_name, words)
            raise SystemExit
        else:
            webbrowser.open(target)
            raise SystemExit

        if words.lower() == "main":
            open_main_website(target)
        if words.lower() == "me" and "github" in target:
            open_main_website(target, "engrbugs")

        webbrowser.open(target.format(words=words))
        return


def print_shortcuts() -> None:
    visible_shortcut_count = count_visible_shortcuts(SHORTCUTS)
    shortcut_titles = [title for title, value in SHORTCUTS.items() if value and value[-1] is not False]

    def format_default(option: str) -> str:
        return f"{option}*" if option == DEFAULT_OPTION else option

    print(f"*Default v{VERSION}")
    for index, title in enumerate(shortcut_titles):
        shortcut = SHORTCUTS[title]
        display_text = f"[{format_default(shortcut[1])}]{title}"
        if visible_shortcut_count == 3 and len(shortcut) > 2 and not shortcut[2]:
            continue
        if index == len(shortcut_titles) - 1:
            print(display_text, end=">    ")
        elif index % 2 == 0:
            print(display_text, end=", ")
        else:
            print(display_text)


def get_matched_shortcut_key(inputted_string: str) -> str | None:
    shortcut_keys: list[str] = []
    for value in SHORTCUTS.values():
        for element in value[1:]:
            if not isinstance(element, bool):
                shortcut_keys.append(element.lower())

    for shortcut_key in sorted(shortcut_keys, key=len, reverse=True):
        if inputted_string.startswith(shortcut_key):
            return shortcut_key
    return None


def main() -> None:
    print_shortcuts()

    inputted_string = input().strip().lower()
    matched_key = get_matched_shortcut_key(inputted_string)

    if matched_key:
        remainder = inputted_string[len(matched_key) :].strip()
        browse(matched_key, remainder)
        return

    if inputted_string == "exit":
        raise SystemExit

    browse(DEFAULT_OPTION, inputted_string)


if __name__ == "__main__":
    main()
