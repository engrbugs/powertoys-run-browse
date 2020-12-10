#! /usr/bin/env python3

"""Launching web browsers for PowerToys Run"""
# Maintained by engrbugs.

import re
import webbrowser


def browse(choice, words):
    print(f'open, {choice}, {words}')
    if re.match(r'[1qazQAZ]', choice):
        webbrowser.open(f'https://www.google.com/search?q={words}')
    if re.match(r'[2wsxWSX]', choice):
        webbrowser.open(f'https://www.thesaurus.com/browse/{words}')
    if re.match(r'[3edcEDC]', choice):
        webbrowser.open(f'https://www.youtube.com/results?search_query={words}')


if __name__ == '__main__':
    print('[1]Google,[2]Thesaurus,[3]Youtube', end=">")
    inputted_string = input()
    x = inputted_string.strip()
    if re.match(r'^[1-3]|[qweQWE]|[asdASD]|[zxcZXC]', x):
        browse(x[0:1], x[1:len(x)].strip())
