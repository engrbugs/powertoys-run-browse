#! /usr/bin/env python3
import re
import webbrowser

"""Launching web browsers for PowerToys Run"""
version = '1.0.6'
default_options = '1'

SHORTCUTS = {
    "Define": ['https://www.google.com/search?q={words} define', '1', 'q'],
    "Thesaurus": ['https://www.google.com/search?q={words} thesaurus', '2', 'w'],
    "Youtube": ['https://www.youtube.com/results?search_query={words}', '3', 'y'],
    "Reverse Dictionary": ['https://www.onelook.com/reverse-dictionary.shtml?s={words}', '4', 'q'],
    "Google Pronunciation": ['https://www.google.com/search?q={words} pronunciation', '5', 'p'],
    "Github": ['https://github.com/search?q={words}', '6', 'g'],
    "stackoverflow": ['https://stackoverflow.com/search?q={words}', '7', 's'],
    "Calendar": ['https://www.google.com/search?q={words} define', '8', 'c'],
    "Reddit": ['https://www.reddit.com/', 'R'],
    "Twitter": ['https://www.twitter.com/', 'T'],
}
# Maintained by engrbugs.


def browse(browse_choice, words):
    print(f'opening, {browse_choice}, {words}')
    for k in SHORTCUTS:
        if any(a in SHORTCUTS[k] for a in [browse_choice.lower(), browse_choice.upper()]):
            if '{' in SHORTCUTS[k][0]:
                # check '#' character in choice replace it with %23 if found. for C#
                if '#' in words:
                    google_word = ''
                    for c in words:
                        google_word += '%23' if c == '#' else c
                    words = google_word
                if words == '':
                    print('What to search', end=":                        ")
                    words = input()
                if words == 'main':
                    main_website = SHORTCUTS[k][0][:SHORTCUTS[k][0].find('/', 9)+1]
                    webbrowser.open(main_website)
                    quit()
                webbrowser.open(SHORTCUTS[k][0].format(words=words))
            else:
                webbrowser.open(SHORTCUTS[k][0])


if __name__ == '__main__':

    #   PAINT SCREEN
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

    #   INPUT MODE
    inputted_string = input()
    inputted_string = inputted_string.strip()

    # OLD REGEX : re.match(r'(?i)^[1-7]$|^[qwep]$|^[asdf]$|^[gty]$|^[r]$', inputted_string)
    # Put all shortcuts in one string
    regex = ''
    for i in SHORTCUTS.items():
        for ii in i[1][1:]:
            regex += ii

    if re.match(fr'(?i)^([{regex}])|\s', inputted_string):
        browse(inputted_string[0:1], inputted_string[1:len(inputted_string)].strip())
    elif inputted_string.lower() == 'exit':
        quit()
    else:
        #  Search with default option--Google.
        browse(default_options, inputted_string)
