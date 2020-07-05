CKEDITOR.disableAutoInline = true;

CKEDITOR.plugins.addExternal( 'codemirror', '/static/newsroom/js/ckeditor/plugins/codemirror/', 'plugin.js' );

CKEDITOR.plugins.addExternal( 'saveedits', '/static/newsroom/js/ckeditor/plugins/saveedits/', 'plugin.js' );

CKEDITOR.plugins.addExternal( 'find', '/static/newsroom/js/ckeditor/plugins/find/', 'plugin.js' );


document.addEventListener("DOMContentLoaded", function(event) {
    document.getElementById("article__statistics").textContent =
        "Words: " + total_words(document.getElementById("article_body")) + ", " +
        "Billable: " + billable_words(document.getElementById("article_body"));
    document.getElementById("article_body").
        addEventListener("input", function() {
            document.getElementById("article__statistics").textContent =
                "Words: " + total_words(document.
                                        getElementById("article_body")) + ", " +
                "Billable: " + billable_words(document.
                                              getElementById("article_body"));
        }, false);
});
