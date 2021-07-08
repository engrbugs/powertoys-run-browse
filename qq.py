#! /usr/bin/env python3
import re
import webbrowser

"""Launching web browsers for PowerToys Run"""
version = '1.0.2'


# Maintained by engrbugs.


def browse(choice, words):
    print(f'opening, {choice}, {words}')
    if re.match(r'[1qQ]', choice):
        # check '#' character in choice replace it with %23 if found.
        google_word = ''
        for c in words:
            google_word += '%23' if c == '#' else c
        webbrowser.open(f'https://www.google.com/search?q={google_word}')
    elif re.match(r'[2]', choice):
        webbrowser.open(f'https://www.thesaurus.com/browse/{words}')
    elif re.match(r'[3yY]', choice):
        if words == 'main':
            webbrowser.open(f'https://www.youtube.com')
        else:
            webbrowser.open(f'https://www.youtube.com/results?search_query={words}')
    elif re.match(r'[4]', choice):
        webbrowser.open(f'https://www.onelook.com/reverse-dictionary.shtml?s={words}')
    elif re.match(r'[5pP]', choice):
        webbrowser.open(f'https://www.google.com/search?q={words} pronunciation')
    elif re.match(r'[rR]', choice):
        webbrowser.open(f'https://www.reddit.com/')
    elif re.match(r'[6]', choice):
        if words == 'main':
            webbrowser.open(f'https://github.com')
        else:
            webbrowser.open(f'https://github.com/search?q={words}')
    elif re.match(r'[7]', choice):
        if words == 'main':
            webbrowser.open(f'https://stackoverflow.com')
        else:
            webbrowser.open(f'https://stackoverflow.com/search?q={words}')


if __name__ == '__main__':
    print(f'*Default v{version}')  # New Line
    print('[1*]Google,[2]Thesaurus,')
    print('[3]Youtube,[4]Reverse Dictionary')
    print('[5]Goggle Pronunciation [R]Reddit')
    print('[6]Github [7]stackoverflow', end=">    ")

    inputted_string = input()
    #  Clean white spaces from beginning to end.
    x = inputted_string.strip()
    #  When inputted with ONE CHAR, it will ask for what to browse.
    if re.match(r'(?i)^[1-7]$|^[qwep]$|^[asdf]$|^[gty]$|^[r]$', x):
        if x.lower() == 'r':
            browse(x, '')
            quit()
        print('What to search', end=":                        ")
        word = input()
        browse(x, word.strip())
    #  Automatically extract the first char when detects whitespace on the 2nd char
    elif re.match(r'(?i)^([1-7]|[qwep]|[asdf]|[gty])\s', x):
        browse(x[0:1], x[1:len(x)].strip())
    #  Search with default option--Google.
    elif x.lower() == 'exit':
        quit()
    else:
        browse('1', x)
