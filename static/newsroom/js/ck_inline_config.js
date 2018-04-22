CKEDITOR.editorConfig = function( config ) {
    config.toolbarGroups = [
	{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
	{ name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
	{ name: 'links', groups: [ 'links' ] },
	{ name: 'insert', groups: [ 'insert' ] },
	{ name: 'forms', groups: [ 'forms' ] },
	{ name: 'tools', groups: [ 'tools' ] },
	{ name: 'others', groups: [ 'others' ] },
	{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
	{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },

	{ name: 'styles', groups: [ 'styles' ] },
	{ name: 'colors', groups: [ 'colors' ] },
	{ name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
	{ name: 'about', groups: [ 'about' ] },
	{ name: 'tools', groups: [ 'tools' ] }
    ];

    config.extraPlugins = 'find,sourcedialog,saveedits';

    config.removeButtons = 'Underline,Subscript,Cut,Copy,Paste,PasteText,PasteFromWord,Undo,Redo,Table,Maximize,Strike,Outdent,Indent,About,AutoComplete,autoFormat,CommentSelectedRange,UncommentSelectedRange';

    config.stylesSet = 'gu_styles';
    config.scayt_sLang = 'en_GB';
    config.scayt_autoStartup = true;
    config.filebrowserBrowseUrl = '/admin/filebrowser/browse?pop=3';
    config.allowedContent = true;
};
