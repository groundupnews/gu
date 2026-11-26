CKEDITOR.stylesSet.add( 'gu_styles', [
    // Block-level styles
    { name: 'Author', element: 'p',
      attributes: { 'class': 'author-description' } },
    { name: 'Caption', element: 'p',
      attributes: { 'class': 'caption' } },
    { name: 'Correction', element: 'p',
      attributes: { 'class': 'correction' } },
    { name: 'Disclaimer', element: 'p',
      attributes: { 'class': 'disclaimer' } },
    { name: 'Editor summary', element: 'div',
      attributes: { 'class': 'editor-summary' } },
    { name: 'Introduction', element: 'p',
      attributes: { 'class': 'intro' } },
    { name: 'Pullout' , element: 'div',
      attributes: { 'class': 'pquote' } },
    { name: 'SoundCloud', element: 'div',
      attributes: { 'class': 'soundcloud'}},
    { name: 'Subheading', element: 'h2',
      attributes: { 'class': 'subheading' } },
    { name: 'Subheading 2', element: 'h3' },
    { name: 'Subheading 3', element: 'h4' },
] );

// Google Docs headings come with inline styles, strip them on paste
function guCleanPastedHeadings(html) {
    if (!/<h[1-6][\s>]/i.test(html)) {
        return html;
    }
    var template = document.createElement('template');
    template.innerHTML = html;
    var headings = template.content.querySelectorAll('h1, h2, h3, h4, h5, h6');
    for (var i = 0; i < headings.length; i++) {
        var heading = headings[i];
        heading.removeAttribute('style');
        heading.removeAttribute('dir');
        if (/^docs-internal-guid/.test(heading.id)) {
            heading.removeAttribute('id');
        }
        // gdocs wraps everything in font-weight: normal, ditch that too
        var wrappers = heading.querySelectorAll(
            'span, b[style*="normal"], strong[style*="normal"]');
        for (var j = 0; j < wrappers.length; j++) {
            var wrapper = wrappers[j];
            while (wrapper.firstChild) {
                wrapper.parentNode.insertBefore(wrapper.firstChild, wrapper);
            }
            wrapper.parentNode.removeChild(wrapper);
        }
    }
    return template.innerHTML;
}

CKEDITOR.on('instanceReady', function (evt) {
    // 999 = after ckeditor's own filters, right before it inserts
    evt.editor.on('paste', function (pasteEvt) {
        var data = pasteEvt.data;
        if (data && typeof data.dataValue === 'string') {
            data.dataValue = guCleanPastedHeadings(data.dataValue);
        }
    }, null, null, 999);
});
