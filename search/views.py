from django.shortcuts import render
import shlex
import string

# Create your views here.

def cleanSearchString(search_string):
    search_strings = shlex.split(search_string)
    translator = str.maketrans({key: None for key in string.punctuation})
    search_strings = [s.translate(translator) for s in search_strings]
