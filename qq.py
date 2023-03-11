#! /usr/bin/env python3
import re
import webbrowser
from dateutil.parser import parse
import datetime
import clipboard as cp
import time


"""Launching web browsers for PowerToys Run"""
version = '1.0.9'
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
}
chat_gpt_main_website = "https://chat.openai.com/chat"
CHATGPT = {
    '1': ['correct my grammar:\n'],
    '2': ['improve my paragraph'],
    '3': ['make it powerful'],
    '4': ['provide me with a first draft for '],
    '5': ['Summarize this for a high school student:\n'],
    '6': ['what is the difference between '],
    '11': ['correct my grammar without punctuation or quotation marks or anything, but just the revision:\n'],
}


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
            cp.copy_to_clipboard(phrase)
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
    is_default = lambda x: x + "*" if x == default_options else x
    print(f'*Default v{version}')  # New Line
    keys = list(SHORTCUTS)
    for i in range(0, len(SHORTCUTS)):
        s = f'[{is_default(SHORTCUTS[keys[i]][1])}]{keys[i]}'
        if i == len(keys) - 1:
            print(s, end=">    ")
        elif i % 2 == 0:
            print(s, end=", ")
        elif i % 2 == 1:
            print(s)

    #   INPUT MODE
    inputted_string = input().strip()

    # OLD REGEX : re.match(r'(?i)^[1-7]$|^[qwep]$|^[asdf]$|^[gty]$|^[r]$', inputted_string)
    # Put all shortcuts in one string
    regex = ''
    for i in SHORTCUTS.items():
        for ii in i[1][1:]:
            regex += ii

    if re.match(fr'(?i)(^[{regex}]$)|(^[{regex}]\s)', inputted_string):
        browse(inputted_string[0:1], inputted_string[1:len(inputted_string)].strip())
    elif inputted_string.lower() == 'exit':
        quit()
    else:
        #  Search with default option--Google.
        browse(default_options, inputted_string)
