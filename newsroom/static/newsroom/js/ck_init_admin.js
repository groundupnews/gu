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

    textarea_editors = ['id_content', 'id_original_question',
                        'id_answer_for_sender', 'id_full_question', 'id_full_answer'];
    for (var i in textarea_editors) {
        id_editor = '#' + textarea_editors[i];
        if ($(id_editor).length) {
            CKEDITOR.replace(textarea_editors[i], {
	        customConfig: '/static/newsroom/js/ck_config.js'
	    });
        }
    }
});
