
CKEDITOR.editorConfig = function( config ) {
    config.toolbarGroups = [
	{ name: 'editing', groups: [ 'find', 'selection',
                                     'spellchecker', 'editing' ] },
	{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
		{ name: 'forms', groups: [ 'forms' ] },
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
	{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks',
                                       'align', 'bidi', 'paragraph' ] },
	{ name: 'links', groups: [ 'links' ] },
	{ name: 'insert', groups: [ 'insert' ] },
	'/',
	{ name: 'styles', groups: [ 'styles' ] },
	{ name: 'colors', groups: [ 'colors' ] },
	{ name: 'tools', groups: [ 'tools' ] },
	{ name: 'others', groups: [ 'others' ] },
	{ name: 'about', groups: [ 'about' ] },
	{ name: 'document', groups: [ 'document', 'doctools', 'mode' ] }
    ];

    config.removeButtons = 'ExportPdf,NewPage,Preview,Print,Templates,Save,Cut,Copy,Paste,PasteText,PasteFromWord,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,CopyFormatting,JustifyLeft,JustifyCenter,JustifyRight,JustifyBlock,BidiLtr,BidiRtl,Language,PageBreak,About';

    config.extraPlugins = 'find,sourcedialog,indentblock';
    config.removePlugins = 'exportpdf';
    config.stylesSet = 'gu_styles';
    config.scayt_sLang = 'en_GB';
    config.scayt_autoStartup = true;
    config.filebrowserBrowseUrl = '/admin/filebrowser/browse/?pop=3';
    config.filebrowserImageBrowseUrl = '/admin/filebrowser/browse/?pop=3&dir=images';
    config.allowedContent = true;
};
