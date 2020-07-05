function get_body() {
    let body = CKEDITOR.instances.id_body.getData();
    let e = document.createElement('html');
    e.innerHTML = body;
    return e;
}

let total_words = function(elem) {
    const word_array = elem.innerText.split(/[\s]+/);
    console.log(word_array);
    const filtered = word_array.filter(function (el) {
        return el != null && el.trim() != "" && el != "&nbsp;";
    });
    return filtered.length;
}

let billable_words = function(elem) {


    /* This gets all paragraphs without captions or not in pquotes and all
       unordered lists that are not the third child (i.e. the first set of
       bullets under the primary image and caption. Also nothing in
       editor-summary is counted.
    */
    let elems = elem.querySelectorAll(
        ":not(.editor-summary) p:not(.caption):not(.pquote):not(.correction):not(.author-description):not(.disclaimer), ul:not(:nth-child(3))");
    let words = 0;
    for (const elem of elems) {
        word_array = elem.innerText.split(/[\s]+/);
        const filtered = word_array.filter(function (el) {
            return el != null && el.trim() != "" && el != "&nbsp;";
        });
        words += filtered.length;
    }
    return words;
}
