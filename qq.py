#! /usr/bin/env python3
import re
import webbrowser

"""Launching web browsers for PowerToys Run"""
version = 0.721
# Maintained by engrbugs.


def browse(choice, words):
    print(f'opening, {choice}, {words}')
    if re.match(r'[1qagQAG]', choice):
        webbrowser.open(f'https://www.google.com/search?q={words}')
    if re.match(r'[2wstWST]', choice):
        webbrowser.open(f'https://www.thesaurus.com/browse/{words}')
    if re.match(r'[3edyEDY]', choice):
        webbrowser.open(f'https://www.youtube.com/results?search_query={words}')
    if re.match(r'[4rfRF]', choice):
        webbrowser.open(f'https://www.onelook.com/reverse-dictionary.shtml?s={words}')


if __name__ == '__main__':
    print(f'*Default v{version}')  # New Line
    print('[1*]Google,[2]Thesaurus,')
    print('[3]Youtube,[4]Reverse Dictionary', end=">    ")
    inputted_string = input()
    #  Clean white spaces from beginning to end.
    x = inputted_string.strip()
    #  When inputted with ONE CHAR, it will ask for what to browse.
    if re.match(r'(?i)^[1-4]$|^[qwe]$|^[asdf]$|^[gtyr]$', x):
        print('What to search', end=":                        ")
        word = input()
        browse(x, word.strip())
    #  Automatically extract the first char when detects whitespace on the 2nd char
    elif re.match(r'(?i)^([1-4]|[qwe]|[asdf]|[gtyr])\s', x):
        browse(x[0:1], x[1:len(x)].strip())
    #  Search with default option--Google.
    else:
        browse('1', x)
