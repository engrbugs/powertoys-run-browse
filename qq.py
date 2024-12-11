#! /usr/bin/env python3
import re
import webbrowser
from dateutil.parser import parse
import datetime
import clipboard as cp
import time
import pyperclip

"""Launching web browsers for PowerToys Run"""
version = '1.2.1'
default_options = '1'

SHORTCUTS = {
    "Define": ['https://www.google.com/search?q={words} define', '1', 'q'],
    "Thesaurus": ['https://www.google.com/search?q={words} thesaurus', '2', 'w'],
    "Youtube": ['https://www.youtube.com/results?search_query={words}', '3', 'y'],
    "Reverse Dictionary": ['https://www.onelook.com/reverse-dictionary.shtml?s={words}', '4', 'q'],
    "Google Pronunciation": ['https://www.google.com/search?q={words} pronunciation', '5', 'p'],
    "Github": ['https://github.com/search?q={words}', '6', 'g'],
    "stackoverflow": ['https://stackoverflow.com/search?q={words}', '7', 's'],
    "Calendar": ['https://calendar.google.com/calendar/u/0/r/day/{words}', '8'],
    "Reddit": ['https://www.reddit.com/', 'R'],
    "Twitter": ['https://www.twitter.com/', 'T'],
    "Ludwig": ['https://ludwig.guru/s/{words}', '9', 'L'],
    "Bible": ['https://www.biblegateway.com/quicksearch/?quicksearch={words}&version=NIV', 'B'],
    "Chat-GPT": ['[chat_gpt]', 'C'],
    "GrammarGPT": ['[GrammarGPT]', 'C1', False]  # False is the visibility (typical)
}
chat_gpt_main_website = "https://chat.openai.com/chat"
#  (X) marks the spot for pyperclip

CHATGPT: {
    "1": ["Please correct my grammar:\n(X)"],
    "11": ["Correct my grammar and provide only the corrected text without introductions or conclusions:\n"],
    "2": ["Improve my paragraph"],
    "3": ["Make this more impactful"],
    "4": ["(X)\nDraft an email addressing the above context with these response points:"],
    "5": ["Summarize this for a high school student:\n"],
    "55": ["Explain this to me like I’m a five-year-old"],
    "6": ["What is the difference between "]
}


CHATGPT = {
    '1': ['Please correct my grammar:\n(X)'],
    '2': ['Improve my paragraph'],
    '3': ['Make that powerful'],
    '4': ["(X)\nCompose an email draft that addresses the above context. Here's the response points:"],
    '5': ['Summarize this for a high school student:\n'],
    '55': ["Explain that to me like I’m a five-year-old kid"],
    '6': ['What is the difference between '],
}


def count_visible_shortcuts(shortcuts_dict):
    count = 0
    for value in shortcuts_dict.values():
        # Check if the last element exists and is not False
        if value and value[-1] is not False:
            count += 1
    return count

def GrammarGPT(words):
    if words == '':
        print('What to put in clipboard')
        for key, value in CHATGPT.items():
            print(key, value)
        print('pick number', end=":                        ")
        words = input().strip()

    text_in_clipboard = pyperclip.paste()
    cp.copy_to_clipboard(CHATGPT['1'].replace("(X)", text_in_clipboard))


# Maintained by engrbugs.
def chat_gpt(words):
    if words == '':
        print('What to put in clipboard')
        for key, value in CHATGPT.items():
            print(key, value)
        print('pick number', end=":                        ")
        words = input().strip()

    if words in CHATGPT:
        for phrase in CHATGPT[words]:
            text_in_clipboard = pyperclip.paste()
            cp.copy_to_clipboard(phrase.replace("(X)",text_in_clipboard))
            if len(CHATGPT[words]) != 1:
                time.sleep(1)

    #  webbrowser.open(chat_gpt_main_website)


def open_main_website(link, append=''):
    main_website = link[:link.find('/', 9) + 1]
    webbrowser.open(main_website + append)
    quit()


def run_function(func_name, *args):
    return globals()[func_name](*args)


def browse(browse_choice, words):
    print(f'opening, {browse_choice}, {words}')
    for k in SHORTCUTS:
        if any(a in SHORTCUTS[k] for a in [browse_choice.lower(), browse_choice.upper()]):
            if '{' in SHORTCUTS[k][0]:
                if k == 'Calendar':
                    okay = None
                    while okay is None:
                        if words == '' or words == 'main':
                            main_website = SHORTCUTS[k][0][:SHORTCUTS[k][0].rfind('/')].replace('day', 'month')
                            webbrowser.open(main_website)
                            quit()
                        try:
                            date = parse(words)
                            words = date.strftime('%Y/%#m/%#d')
                            break
                        except:
                            today = datetime.date.today()
                            if words.lower() == 'today' or words.lower() == 'now':
                                today = datetime.date.today()
                                words = today.strftime('%Y/%#m/%#d')
                            elif words.lower() == 'yesterday' or words.lower() == 'yday':
                                yesterday = today - datetime.timedelta(days=1)
                                words = yesterday.strftime('%Y/%#m/%#d')
                                print(words)
                            elif words.lower() == 'tomorrow' or words.lower() == 'tom':
                                tomorrow = today + datetime.timedelta(days=1)
                                words = tomorrow.strftime('%Y/%#m/%#d')
                            else:
                                print('Cannot read date')
                                print('Please enter new date or press ENTER for month)', end=":    ")
                                words = input()
                # check '#' character in choice replace it with %23 if found. for C#
                if '#' in words:
                    google_word = ''
                    for c in words:
                        google_word += '%23' if c == '#' else c
                    words = google_word
                if words == '':
                    print('What to search', end=":                        ")
                    words = input().strip()
                    if words == "":
                        words = 'main'
            elif '[' in SHORTCUTS[k][0]:
                function_name = SHORTCUTS[k][0].replace("[", "").replace("]", "")
                run_function(function_name, words)
                quit()
            else:
                webbrowser.open(SHORTCUTS[k][0])
                quit()
            if words.lower() == 'main':
                open_main_website(SHORTCUTS[k][0])
            elif words.lower() == 'me' and 'github' in SHORTCUTS[k][0]:
                open_main_website(SHORTCUTS[k][0], 'engrbugs')
            else:
                webbrowser.open(SHORTCUTS[k][0].format(words=words))


if __name__ == '__main__':
    #   PAINT SCREEN
    len_shortcuts_shown = count_visible_shortcuts(SHORTCUTS)
    is_default = lambda x: x + "*" if x == default_options else x
    print(f'*Default v{version}')  # New Line
    shortcut_titles = [title for title, value in SHORTCUTS.items() if value and value[-1] is not False]
    for i in range(0, len_shortcuts_shown):
        s = f'[{is_default(SHORTCUTS[shortcut_titles[i]][1])}]{shortcut_titles[i]}'
        if len_shortcuts_shown == 3 and not SHORTCUTS[shortcut_titles[i]][2]:
            pass
        else:
            if i == len(shortcut_titles) - 1:
                print(s, end=">    ")
            elif i % 2 == 0:
                print(s, end=", ")
            elif i % 2 == 1:
                print(s)

    #   INPUT MODE
    inputted_string = input().strip().lower()

    shortcut_keys = []
    for key, value in SHORTCUTS.items():
        for element in value[1:]:
            if not isinstance(element, bool):
                shortcut_keys.append(element.lower())

    if inputted_string.split(' ')[0] in shortcut_keys:
        browse(inputted_string[0:1], inputted_string[1:len(inputted_string)].strip())
    elif inputted_string.lower() == 'exit':
        quit()
    else:
        #  Search with default option--Google.
        browse(default_options, inputted_string)
