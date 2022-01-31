CKEDITOR.plugins.add( 'saveedits', {
    icons: 'saveedits',
    init: function( editor ) {
	editor.ui.addButton( 'SaveEdits', {
	    label: 'Save',
	    command: 'saveedits',
	    toolbar: 'document'
	});
	editor.addCommand( 'saveedits',  {
	    exec: function(editor) {
		document.getElementById("saveedits").click();
            }
	});
    }
});
