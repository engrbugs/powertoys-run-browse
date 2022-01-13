#! /usr/bin/env python3
import re
import webbrowser

"""Launching web browsers for PowerToys Run"""
version = '1.0.3'
default_options = '2'



# Maintained by engrbugs.


def browse(browse_choice, words):
    print(f'opening, {browse_choice}, {words}')
    if re.match(r'[1qQ]', browse_choice):
        # check '#' character in choice replace it with %23 if found.
        google_word = ''
        for c in words:
            google_word += '%23' if c == '#' else c
        webbrowser.open(f'https://www.google.com/search?q={google_word}')
    elif re.match(r'[2]', browse_choice):
        webbrowser.open(f'https://www.thesaurus.com/browse/{words}')
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
    options = lambda x: x + "*" if x == default_options else x
    print(f'*Default v{version}')  # New Line
    print(f'[{options("1")}]Google,'
          f'[{options("2")}]Thesaurus')
    print(f'[{options("3")}]Youtube,'
          f'[{options("4")}]Reverse Dictionary')
    print(f'[{options("5")}]Goggle Pronunciation,'
          f'[{options("R")}]Reddit')
    print(f'[{options("6")}]Github,'
          f'[{options("7")}]stackoverflow', end=">    ")

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
