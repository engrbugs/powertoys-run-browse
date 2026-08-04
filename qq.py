#! /usr/bin/env python3
"""Launch web browsers and prompt helpers for PowerToys Run."""

from __future__ import annotations

import datetime
import json
import itertools
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

import clipboard as cp
import pyperclip
from dateutil.parser import parse

VERSION = "1.2.2"
DEFAULT_OPTION = "1"

try:
    import config as user_config
except ImportError:
    user_config = None


def config_value(name: str, default: object) -> object:
    return getattr(user_config, name, default) if user_config else default


# Override these values in config.py for a local LLM or compatible API endpoint.
SERVER_URL = str(config_value("SERVER_URL", "http://192.168.1.88:5000"))
TARGET_TPS = int(config_value("TARGET_TPS", 50))
LLM_MODEL = str(config_value("LLM_MODEL", "local-model"))
DEFAULT_CONTEXT_TOKENS = int(config_value("DEFAULT_CONTEXT_TOKENS", 8192))
MAX_INPUT_CONTEXT_RATIO = float(config_value("MAX_INPUT_CONTEXT_RATIO", 0.4))
EXIT_PAUSE_SECONDS = float(config_value("EXIT_PAUSE_SECONDS", 2))


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
    "LLM AutoGrammar": ["[llm_auto_grammar]", "X1", True],
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


def build_auto_grammar_prompt(text: str, context: str = "") -> str:
    context_line = f"\nContext: {context.strip()}" if context.strip() else ""
    return f"""You are an autocorrect engine.

Correct the grammar, spelling, punctuation, and capitalization in the clipboard text.
Preserve the original meaning, tone, names, links, code, formatting, line breaks, context, and intent.
Stay true to the source context, even when the text is crude, derogatory, informal, or uncomfortable.
Return only the corrected text. Do not add explanations, labels, quotes, or Markdown fences.{context_line}

Clipboard text:
{text}"""


def post_json(endpoint: str, payload: dict[str, object], timeout: int = 120) -> dict[str, object]:
    request = urllib.request.Request(
        f"{SERVER_URL.rstrip('/')}{endpoint}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(endpoint: str, timeout: int = 10) -> dict[str, object] | list[object]:
    request = urllib.request.Request(
        f"{SERVER_URL.rstrip('/')}{endpoint}",
        headers={"Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def find_context_tokens(value: object) -> int | None:
    context_keys = {
        "n_ctx",
        "nctx",
        "num_ctx",
        "numctx",
        "ctx_size",
        "ctxsize",
        "context_length",
        "contextlength",
        "max_context_length",
        "maxcontextlength",
    }

    if isinstance(value, dict):
        for key, item in value.items():
            normalized_key = key.lower().replace(".", "_").replace("-", "_")
            compact_key = normalized_key.replace("_", "")
            is_context_key = (
                normalized_key in context_keys
                or compact_key in context_keys
                or ("context" in compact_key and ("length" in compact_key or "size" in compact_key))
            )
            if is_context_key:
                if isinstance(item, int) and item > 0:
                    return item
                if isinstance(item, str) and item.isdigit():
                    return int(item)

            found = find_context_tokens(item)
            if found:
                return found

    if isinstance(value, list):
        for item in value:
            found = find_context_tokens(item)
            if found:
                return found

    return None


def detect_model_context_tokens() -> int:
    attempts: list[tuple[str, str, dict[str, object] | None]] = [
        ("GET", "/props", None),
        ("GET", "/slots", None),
        ("POST", "/api/show", {"model": LLM_MODEL}),
    ]

    for method, endpoint, payload in attempts:
        try:
            response = get_json(endpoint, timeout=10) if method == "GET" else post_json(endpoint, payload or {}, timeout=10)
            context_tokens = find_context_tokens(response)
            if context_tokens:
                return context_tokens
        except (OSError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError, ValueError, json.JSONDecodeError):
            continue

    return DEFAULT_CONTEXT_TOKENS


def estimate_token_count(text: str) -> int:
    return max(1, len(text) // 4)


def pause_before_exit() -> None:
    time.sleep(EXIT_PAUSE_SECONDS)


class ConsoleRunner:
    def __init__(self, label: str) -> None:
        self.label = label
        self.started_at = time.monotonic()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._spin, daemon=True)

    def __enter__(self) -> "ConsoleRunner":
        print(self.label)
        self._thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self.stop()

    def _spin(self) -> None:
        for frame in itertools.cycle("|/-\\"):
            if self._stop_event.is_set():
                break
            elapsed = time.monotonic() - self.started_at
            sys.stdout.write(f"\r{frame} LLM is fixing... {elapsed:0.1f}s")
            sys.stdout.flush()
            time.sleep(0.2)

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=1)
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()

    def done(self, text: str) -> None:
        self.stop()
        elapsed = max(0.001, time.monotonic() - self.started_at)
        output_tokens = estimate_token_count(text)
        print(f"LLM done in {elapsed:0.1f}s | output: ~{output_tokens} tokens | ~{output_tokens / elapsed:0.1f} TPS")


def available_generation_tokens(prompt: str) -> tuple[int, int, int, int]:
    context_tokens = detect_model_context_tokens()
    prompt_tokens = estimate_token_count(prompt)
    input_cap_tokens = int(context_tokens * MAX_INPUT_CONTEXT_RATIO)
    reserved_tokens = prompt_tokens + 256
    response_tokens = max(256, min(DEFAULT_CONTEXT_TOKENS, context_tokens - reserved_tokens))
    return response_tokens, prompt_tokens, context_tokens, input_cap_tokens


def extract_llm_text(response: dict[str, object]) -> str:
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        first_choice = choices[0]
        if isinstance(first_choice, dict):
            message = first_choice.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(first_choice.get("text"), str):
                return first_choice["text"]

    for key in ("content", "response", "generated_text", "text"):
        value = response.get(key)
        if isinstance(value, str):
            return value

    raise ValueError("LLM response did not contain generated text")


def request_llm_fix(prompt: str, clipboard_tokens: int) -> str:
    print("Detecting model context window...")
    generation_tokens, prompt_tokens, context_tokens, input_cap_tokens = available_generation_tokens(prompt)
    attempts: list[tuple[str, dict[str, object]]] = [
        (
            "/v1/chat/completions",
            {
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": generation_tokens,
            },
        ),
        (
            "/completion",
            {
                "prompt": prompt,
                "temperature": 0,
                "n_predict": generation_tokens,
            },
        ),
        (
            "/api/generate",
            {
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0, "num_predict": generation_tokens},
            },
        ),
    ]

    last_error: Exception | None = None
    print(f"Detected model context: {context_tokens} tokens x {MAX_INPUT_CONTEXT_RATIO:.0%} cap for output")
    print(f"Actual clipboard tokens: ~{clipboard_tokens} tokens")
    if prompt_tokens > input_cap_tokens:
        raise ValueError(
            "Clipboard plus instructions are above the safe input cap. "
            "Not sending request."
        )
    if prompt_tokens >= context_tokens:
        raise ValueError(
            "Clipboard plus instructions are larger than the detected model context. "
            "Not sending request."
        )
    elif prompt_tokens + generation_tokens > context_tokens:
        print("NOTE: Response tokens were reduced to fit inside the detected context window.")
    for endpoint, payload in attempts:
        print(f"Trying {endpoint}")
        runner = ConsoleRunner(f"LLM is fixing via {endpoint}...")
        try:
            runner.__enter__()
            fixed_text = extract_llm_text(post_json(endpoint, payload)).strip()
            runner.done(fixed_text)
            return fixed_text
        except (OSError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError, ValueError) as error:
            runner.stop()
            print(f"{endpoint} failed: {error}")
            last_error = error

    raise RuntimeError(f"LLM request failed: {last_error}")


def llm_auto_grammar(words: str) -> None:
    text_in_clipboard = pyperclip.paste()
    if not text_in_clipboard.strip():
        print("Clipboard is empty")
        pause_before_exit()
        return

    prompt = build_auto_grammar_prompt(text_in_clipboard, words)
    clipboard_tokens = estimate_token_count(text_in_clipboard)
    try:
        fixed_text = request_llm_fix(prompt, clipboard_tokens)
    except ValueError as error:
        print(error)
        pause_before_exit()
        return
    if fixed_text:
        cp.copy_to_clipboard(fixed_text)
        print("Corrected text copied to clipboard")
    else:
        print("LLM returned an empty correction")
    pause_before_exit()


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
    groups = {
        "Search": [
            "Define",
            "Thesaurus",
            "Youtube",
            "Reverse Dictionary",
            "Google Pronunciation",
            "Github",
            "stackoverflow",
            "Ludwig",
            "Bible",
        ],
        "Open": ["Calendar", "Reddit", "Twitter"],
        "Clipboard + AI": ["Chat-GPT", "GrammarGPT", "LLM AutoGrammar"],
    }

    print(f"PowerToys Run Browse v{VERSION}")
    print("Type a shortcut, optionally followed by a phrase.")
    print("Examples:  g python pathlib   |   y ambient music   |   X1")
    print()

    for group_name, titles in groups.items():
        entries = []
        for title in titles:
            shortcut = SHORTCUTS[title]
            key = shortcut[1]
            marker = "*" if key == DEFAULT_OPTION else ""
            entries.append(f"{key}{marker} {title}")
        print(f"{group_name}: " + "  ·  ".join(entries))

    print("\nReady > ", end="", flush=True)


def get_matched_shortcut_key(inputted_string: str) -> str | None:
    shortcut_keys: list[str] = []
    for value in SHORTCUTS.values():
        for element in value[1:]:
            if not isinstance(element, bool):
                shortcut_keys.append(element.lower())

    for shortcut_key in sorted(shortcut_keys, key=len, reverse=True):
        if inputted_string == shortcut_key:
            return shortcut_key
        if inputted_string.startswith(shortcut_key + " "):
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
