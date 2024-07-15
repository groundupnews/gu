CKEDITOR.editorConfig = function( config ) {
    config.toolbarGroups = [
	{ name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
	{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
	{ name: 'forms', groups: [ 'forms' ] },
	{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
	{ name: 'links', groups: [ 'links' ] },
	{ name: 'insert', groups: [ 'insert' ] },
	{ name: 'styles', groups: [ 'styles' ] },
	{ name: 'colors', groups: [ 'colors' ] },
	{ name: 'tools', groups: [ 'tools' ] },
	{ name: 'others', groups: [ 'others' ] },
	{ name: 'about', groups: [ 'about' ] }
    ];

    config.extraPlugins = 'find,sourcedialog,indentblock,';
    config.removePlugins =
        'contextmenu,liststyle,tabletools,tableselection,exportpdf';

    config.removeButtons = 'NewPage,Save,ExportPdf,Preview,Print,Cut,Copy,Paste,PasteText,PasteFromWord,Find,Replace,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,CopyFormatting,NumberedList,BulletedList,Outdent,Indent,Blockquote,CreateDiv,JustifyLeft,JustifyCenter,JustifyRight,JustifyBlock,BidiLtr,BidiRtl,Language,Anchor,Image,Table,HorizontalRule,PageBreak,Iframe,Styles,Format,Maximize,ShowBlocks,About,Templates,Scayt';

    // config.scayt_sLang = 'en_GB';
    config.scayt_autoStartup = false;
    config.disableNativeSpellChecker = false;
    config.htmlEncodeOutput = false;
    config.entities = false;
    config.versionCheck = false;
    // config.enterMode = CKEDITOR.ENTER_BR;
};
