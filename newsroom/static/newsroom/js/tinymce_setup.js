
function CustomFileBrowser(field_name, url, type, win) {

    var cmsURL = '/admin/filebrowser/browse/?pop=2';
    if (type == "image") {
	cmsURL = cmsURL + '&dir=images';
    }

    tinyMCE.activeEditor.windowManager.open({
        file: cmsURL,
        width: 980,  // Your dimensions may differ - toy around with them!
        height: 500,
        resizable: 'yes',
        scrollbars: 'yes',
        inline: 'no',  // This parameter only has an effect if you use the inlinepopups plugin!
        close_previous: 'no'
    }, {
        window: win,
        input: field_name,
        editor_id: tinyMCE.selectedInstance.editorId
    });
    return false;
}

tinyMCE.init({

    // see http://www.tinymce.com/wiki.php/Configuration

    // Init
    mode: 'textareas',
    theme: 'advanced',
    skin: 'grappelli',

    // General
    accessibility_warnings: false,
    browsers: 'gecko,msie,safari,opera',
    dialog_type: 'window',
    editor_deselector: 'mceNoEditor',
    keep_styles: false,
    language: 'en',
    object_resizing: false,
    plugins: 'advimage,advlink,codemagic,fullscreen,paste,media,searchreplace,grappelli,table,template',
    // directionality : "rtl",

    // Callbacks
    file_browser_callback: 'CustomFileBrowser',

    // Cleanup/Output
    element_format: 'xhtml',
    fix_list_elements: true,
    forced_root_block: 'p',
    valid_elements : '*[*]',
    //extended_valid_elements : 'iframe[class|id|src|border|alt|title|hspace|vspace|frameborder|allowfullscreen|width|height|align|name],aside[class|id]',
    // style formsts overrides theme_advanced_styles
    // see http://www.tinymce.com/wiki.php/Configuration:style_formats
    style_formats: [
        {title: 'Pullout quote', block : 'aside', classes: 'pquote'},
        {title: 'Introduction', block : 'p', classes: 'intro'},
        {title: 'Full width image', block : 'div', classes: 'full-width'},
        {title: 'Very large image', block : 'div', classes: 'very-large'},
        {title: 'Image caption', block : 'p', classes: 'caption'},
        {title: 'Subheading', block : 'h3', classes: 'subheading'},
        {title: 'Author description', block : 'p', classes:'author-description'},
        {title: 'Disclaimer', block : 'p', classes: 'disclaimer'},
        {title: 'Correction', block : 'p', classes: 'correction'},
        {title: 'Summary', block : 'p', classes: 'summary-text'}
    ],
    verify_html: true,

    // URL
    relative_urls: false,
    remove_script_host: true,

    // Layout
    width: "800px",
    height: "500px",
    indentation: '20px',

    // Content CSS
    // customize your content ...
    content_css : "/static/newsroom/css/newsroom_tinymce.css",


    // Theme Advanced
    theme_advanced_toolbar_location: 'top',
    theme_advanced_toolbar_align: 'left',
    theme_advanced_statusbar_location: 'bottom',
    theme_advanced_buttons1: 'formatselect,styleselect,|,bold,italic,|,bullist,numlist,|,undo,redo,|,link,unlink,|,image,media,|,fullscreen,|,grappelli_adv',
    theme_advanced_buttons2: 'search,|,pasteword,charmap,|,codemagic,|,table,cleanup,grappelli_documentstructure',
    theme_advanced_buttons3: '',
    theme_advanced_path: false,
    theme_advanced_blockformats: 'p,h1,h2,h3,h4,blockquote,aside,pre',
    theme_advanced_resizing: true,
    theme_advanced_resize_horizontal: true,
    theme_advanced_resizing_use_cookie: true,
    paste_auto_cleanup_on_paste : true,

    // Templates
    // see http://www.tinymce.com/wiki.php/Plugin:template
    // please note that you need to add the URLs (src) to your url-patterns
    // with django.views.generic.simple.direct_to_template
    template_templates : [
        {
            title : '2 Columns',
            src : '/path/to/your/template/',
            description : '2 Columns.'
        },
        {
            title : '4 Columns',
            src : '/path/to/your/template/',
            description : '4 Columns.'
        }
    ],

    // Image Plugin
    // see http://www.tinymce.com/wiki.php/Plugin:advimage
    theme_advanced_styles: 'full-width=full-width;very-large=very-large',
    advimage_update_dimensions_onchange: true,

    // Link Settings
    // see http://www.tinymce.com/wiki.php/Plugin:advlink
    advlink_styles: 'Internal Link=internal;External Link=external',

    // Media Plugin
    // see http://www.tinymce.com/wiki.php/Plugin:media
    media_strict: false,

    // Grappelli Settings
    grappelli_adv_hidden: false,
    grappelli_show_documentstructure: 'on'

});
