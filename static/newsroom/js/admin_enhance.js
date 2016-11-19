var $ = django.jQuery;

$(document).ready(function() {
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
});
