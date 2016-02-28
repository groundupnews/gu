
CKEDITOR.editorConfig = function( config ) {
    config.toolbarGroups = [
	{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
	{ name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
	{ name: 'links', groups: [ 'links' ] },
	{ name: 'insert', groups: [ 'insert' ] },
	{ name: 'forms', groups: [ 'forms' ] },
	{ name: 'tools', groups: [ 'tools' ] },
	{ name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
	{ name: 'others', groups: [ 'others' ] },
	'/',
	{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
	{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },
	{ name: 'styles', groups: [ 'styles' ] },
	{ name: 'colors', groups: [ 'colors' ] },
	{ name: 'about', groups: [ 'about' ] }
    ];

    config.extraPlugins = 'sourcedialog,codemirror,saveedits';

    config.removeButtons = 'Underline,Subscript,Superscript,Cut,Copy,Paste,PasteText,PasteFromWord,Undo,Redo,Link,Unlink,Anchor,Image,Table,HorizontalRule,SpecialChar,Maximize,Bold,Italic,Strike,RemoveFormat,NumberedList,BulletedList,Indent,Outdent,Blockquote,Styles,Format,About,Source,AutoComplete,autoFormat,CommentSelectedRange,UncommentSelectedRange';
    config.scayt_sLang = 'en_GB';
    config.scayt_autoStartup = true;
    config.htmlEncodeOutput = false;
    config.entities = false;
    config.enterMode = CKEDITOR.ENTER_BR;
};
