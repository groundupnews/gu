var $ = django.jQuery;

$(document).ready(function() {

    /* Length of title */
    function title_length() {
	var title_length = $('#id_title').val().length;
	return title_length.toString();
    };

    if($('#id_title').length) {
	$('#id_title').after('<span id="title-length">' +
			     title_length() + '</span>');
    }

    $( "#id_title").on('input propertychange paste', function() {
	$("#title-length").text(title_length());
    });


    /* Billable words */
    CKEDITOR.instances.id_body.on('contentDom', function() {
        $('#cke_wordcount_id_body').after(
            '<span id="billable-words">,&nbsp;Billable: <span id="billable-count">'
                + billable_words(get_body()) + '</span></span>');
    });
    CKEDITOR.instances.id_body.on('change', function() {
        $('#billable-count').html(billable_words(get_body()));
    });
});
