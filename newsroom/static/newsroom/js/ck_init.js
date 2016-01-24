CKEDITOR.disableAutoInline = true;

/*CKEDITOR.plugins.addExternal( 'codemirror', '/static/newsroom/js/ckeditor/plugins/codemirror/', 'plugin.js' );*/

CKEDITOR.plugins.addExternal( 'saveedits', '/static/newsroom/js/ckeditor/plugins/saveedits/', 'plugin.js' );

CKEDITOR.stylesSet.add( 'gu_styles', [
    // Block-level styles
    { name: 'Paragraph', element: 'p'},
    { name: 'Image', element: 'figure',
      attributes: { 'class': 'full-width' } },
    { name: 'Large Image', element: 'figure',
      attributes: { 'class': 'very-large' } },
    { name: 'Image Caption', element: 'figcaption',
      attributes: { 'class': 'caption' } },
    { name: 'Introduction', element: 'p',
      attributes: { 'class': 'intro' } },
    { name: 'Pullout Quote' , element: 'aside',
      attributes: { 'class': 'pquote' } }
] );
