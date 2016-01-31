CKEDITOR.plugins.addExternal( 'codemirror', '/static/newsroom/js/ckeditor/plugins/codemirror/', 'plugin.js' );

CKEDITOR.plugins.addExternal( 'find', '/static/newsroom/js/ckeditor/plugins/find/', 'plugin.js' );

CKEDITOR.plugins.addExternal( 'wordcount', '/static/newsroom/js/ckeditor/plugins/wordcount/', 'plugin.js' );


var $ = django.jQuery;

$(document).ready(function() {
    function ckeditor_switch() {
	if ($("#id_use_editor").prop('checked')) {
	    CKEDITOR.replace( 'id_body', {
		customConfig: '/static/newsroom/js/ck_config.js'
	    });
	    CKEDITOR.replace( 'id_summary_text', {
		customConfig: '/static/newsroom/js/ck_config.js'
	    });
	    CKEDITOR.replace( 'id_copyright', {
		customConfig: '/static/newsroom/js/ck_config.js'
	    });
	} else {
	    for(name in CKEDITOR.instances)
	    {
		CKEDITOR.instances[name].destroy(true);
	    }
	}
    }

    if ($( "#id_use_editor").length) {
	$( "#id_use_editor").change( function() {
	    ckeditor_switch();
	});
	ckeditor_switch();
    }

    if ($("#id_content").length) {
	CKEDITOR.replace( 'id_content', {
	    customConfig: '/static/newsroom/js/ck_config.js'
	});
    }
});
