
CKEDITOR.editorConfig = function( config ) {
    config.toolbarGroups = [
	{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
	{ name: 'editing', groups: [ 'find', 'selection', 'spellchecker',
                                     'editing' ] },
	{ name: 'links', groups: [ 'links' ] },
	{ name: 'insert', groups: [ 'insert' ] },
	{ name: 'forms', groups: [ 'forms' ] },
	{ name: 'tools', groups: [ 'tools' ] },
	{ name: 'others', groups: [ 'others' ] },
	{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
	{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align',
                                       'paragraph' ] },

	{ name: 'styles', groups: [ 'styles' ] },
	{ name: 'colors', groups: [ 'colors' ] },
	{ name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
	{ name: 'about', groups: [ 'about' ] },
	{ name: 'tools', groups: [ 'tools' ] }
    ];


    config.extraPlugins = 'find,sourcearea,indentblock,wordcount,uploadimage';
    config.removePlugins =
        'contextmenu,liststyle,tabletools,tableselection,exportpdf';

    config.removeButtons = 'Cut,Copy,Paste,PasteText,PasteFromWord';

    config.stylesSet = 'gu_styles';
    config.scayt_sLang = 'en_GB';
    config.scayt_autoStartup = false;
    config.disableNativeSpellChecker = false;
    config.filebrowserBrowseUrl = '/admin/filebrowser/browse/?pop=3';
    config.filebrowserImageBrowseUrl = '/admin/filebrowser/browse/?pop=3&dir=images';
    config.filebrowserAudioBrowseUrl = '/admin/filebrowser/browse/?pop=3&dir=sound/summaries';
    config.extraAllowedContent = '*(*)';
    config.allowedContent = true;

    config.allowedContent = true;
    config.contentsCss = '/static/newsroom/css/ckeditor_styles.css';
    // Pasted images (e.g. from Word or Google Docs) are uploaded and
    // stored as files instead of being embedded in the article.
    config.uploadUrl = '/article_image_upload/';
    config.fileTools_requestHeaders = {
        'X-CSRFToken': (document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/) || [])[1]
    };
    config.versionCheck = false;
};
