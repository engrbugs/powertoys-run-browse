#! /usr/bin/env python3
import re
import webbrowser

"""Launching web browsers for PowerToys Run"""
version = '1.0.5'
default_options = '1'

SHORTCUTS = {
    "Define": ['https://www.google.com/search?q={words} define', '1', 'q'],
    "Thesaurus": ['https://www.google.com/search?q={words} define', '2', 't'],
    "Youtube": ['https://www.google.com/search?q={words} define', '3', 'y'],
    "Reverse Dictionary": ['https://www.google.com/search?q={words} define', '4', 'q'],
    "Google Pronunciation": ['https://www.google.com/search?q={words} define', '5', 'p'],
    "Github": ['https://www.google.com/search?q={words} define', '6', 'g'],
    "stackoverflow": ['https://www.google.com/search?q={words} define', '7', 's'],
    "Calendar": ['https://www.google.com/search?q={words} define', '8', 'c'],
    "Reddit": ['https://www.google.com/search?q={words} define', 'R'],
    "Twitter": ['https://www.google.com/search?q={words} define', 'T'],
}
# Maintained by engrbugs.


def browse(browse_choice, words):
    print(f'opening, {browse_choice}, {words}')
    if re.match(r'[1qQ]', browse_choice):
        # check '#' character in choice replace it with %23 if found.
        google_word = ''
        for c in words:
            google_word += '%23' if c == '#' else c
        webbrowser.open(f'https://www.google.com/search?q={google_word} define')
    elif re.match(r'[2]', browse_choice):
        webbrowser.open(f'https://www.google.com/search?q={words} thesaurus')
    elif re.match(r'[3yY]', browse_choice):
        if words == 'main':
            webbrowser.open(f'https://www.youtube.com')
        else:
            webbrowser.open(f'https://www.youtube.com/results?search_query={words}')
    elif re.match(r'[4]', browse_choice):
        webbrowser.open(f'https://www.onelook.com/reverse-dictionary.shtml?s={words}')
    elif re.match(r'[5pP]', browse_choice):
        webbrowser.open(f'https://www.google.com/search?q={words} pronunciation')
    elif re.match(r'[rR]', browse_choice):
        webbrowser.open(f'https://www.reddit.com/')
    elif re.match(r'[6]', browse_choice):
        if words == 'main':
            webbrowser.open(f'https://github.com')
        else:
            webbrowser.open(f'https://github.com/search?q={words}')
    elif re.match(r'[7]', browse_choice):
        if words == 'main':
            webbrowser.open(f'https://stackoverflow.com')
        else:
            webbrowser.open(f'https://stackoverflow.com/search?q={words}')


if __name__ == '__main__':

    #   PAINT SCREEN.
    is_default = lambda x: x + "*" if x == default_options else x
    print(f'*Default v{version}')  # New Line
    keys = list(SHORTCUTS)
    for i in range(0, len(SHORTCUTS)):
        s = f'[{is_default(SHORTCUTS[keys[i]][1])}]{keys[i]}'
        if i == len(keys)-1:
            print(s, end=">    ")
        elif i % 2 == 0:
            print(s, end=", ")
        elif i % 2 == 1:
            print(s)

    inputted_string = input()
    #  Clean white spaces from beginning to end.
    inputted_string = inputted_string.strip()
    #  When inputted with ONE CHAR, it will ask for what to browse.
    if re.match(r'(?i)^[1-7]$|^[qwep]$|^[asdf]$|^[gty]$|^[r]$', inputted_string):
        if inputted_string.lower() == 'r':
            browse(inputted_string, '')
            quit()
        print('What to search', end=":                        ")
        word = input()
        browse(inputted_string, word.strip())
    #  Automatically extract the first char when detects whitespace on the 2nd char
    elif re.match(r'(?i)^([1-7]|[qwep]|[asdf]|[gty])\s', inputted_string):
        browse(inputted_string[0:1], inputted_string[1:len(inputted_string)].strip())

    elif inputted_string.lower() == 'exit':
        quit()
    else:
        #  Search with default option--Google.
        browse(default_options, inputted_string)
