#!/usr/bin/env python3

from curses.ascii import isalpha
import random
import sys

import hashlib

from django.conf import settings

def hashCode(str):
    m = hashlib.sha256()
    m.update(bytes(str, 'utf-8'))
    return m.hexdigest()

def hashCode2(str):
    hash = 0
    if len(str) == 0: return hash

    for i in range(0, len(str)):
        chr = ord(str[i])
        hash  = ((hash << 5) - hash) + chr;
        hash |= 0

    print(str, ":", hash)
    return hash


def makeTarget(wordFile="words.txt"):

    STATIC_ROOT = settings.STATIC_ROOT + "target/words/"

    offensive1 = open(STATIC_ROOT + "offensive.1").readlines()
    offensive2 = open(STATIC_ROOT + "offensive.2").readlines()
    profane1 = open(STATIC_ROOT + "profane.1").readlines()
    profane3 = open(STATIC_ROOT + "profane.3").readlines()

    banned = offensive1 + offensive2 + profane1 + profane3

    with open(STATIC_ROOT + wordFile, 'r', errors='replace') as f:
        words = [w[:-1] for w in f.readlines()
             if all(isalpha(c) for c in w[:-1]) and w == w.lower() and
             len(w) > 4 and len(w) < 11 and w not in banned]

    words_9 = [w for w in words if len(w) == 9]


    sorted_words_9 = sorted([''.join(sorted(w)) for w in words_9])


    sorted_words_9_nodups = []
    previous_word = sorted_words_9[0]
    duplicate = False
    for s in sorted_words_9:
        if s != previous_word:
            previous_word = s
            if duplicate == False:
                sorted_words_9_nodups.append(previous_word)
            duplicate = False
        else:
            duplicate = True


    index = random.randint(0, len(sorted_words_9_nodups) - 1)
    letters = sorted(sorted_words_9_nodups[index])
    target_letters = letters.copy()
    random.shuffle(target_letters)

    bullseye = target_letters[0]

    target = ""
    target_words = []
    for word in words:
        if bullseye not in word:
            continue
        sorted_word = sorted(word)
        i = 0
        num_matches = 0
        for c in sorted_word:
            matched = False
            while (i < 9) and (matched == False):
                if c == letters[i]:
                    matched = True
                    num_matches = num_matches + 1
                i = i + 1
            if i == 9:
                break
        l = len(word)
        if num_matches == l:
            target_words.append(word)
            if (l == 9):
                target = word

    return {
            "letters": target_letters,
            "bullseye": bullseye,
            "target": target,
            "words": target_words,
            "hashed_words": [hashCode(w) for w in target_words]
        }

def main():

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "words.txt"
    result = makeTarget(filename)

    print("Target letters:", result["letters"])
    print("Bulls eye:", result["bullseye"])
    print("Target:", result["target"])
    print("Words:", result["words"])
    print("Hashed words:", result["hashed_words"])
    print("Number words", len(result["words"]))


if __name__ == '__main__':
    main()
