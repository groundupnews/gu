"use strict;"

function isAlphaNumeric(w) {
    return w.match(/^[a-z0-9]+$/i) !== null;
}

function makeSlug(text) {
    const ignoreList = [
        "", " ", "a", "an", "the", "of", "and",
        "or", "are", "is", "&nbsp;", "this",
        "that", "there",
    ];
    let words = text.split(' ');
    let keptWords = [];
    for (const word of words) {
        let newWord = "";
        for (const c of word) {
            if (isAlphaNumeric(c) || c == "_" || c == '-') {
                newWord += c;
            }
        }
        if (!ignoreList.includes(newWord)) {
            keptWords.push(newWord.toLowerCase());
        }
    }
    return keptWords.join('-');
}
