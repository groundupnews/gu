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

    var url = document.URL;
    if (url.indexOf("/article/add/") == -1) {
	idx = url.indexOf("/article/") + 9;
	pk = url.slice(idx, -1);
	version = $("#id_version").val();
	timerCheckConcurrency =
	    window.setInterval(function(){
		$.ajax({
		    url: "/article/concurrent/" + pk + "/" + version,
		    type:"GET",
		    success: function(user){
			if (user != "(None)") {
			    clearTimeout(timerCheckConcurrency);
			    $("form :input").attr("disabled","disabled");
			    for(name in CKEDITOR.instances) {
				CKEDITOR.instances[name].setReadOnly();
			    }
			    msg = "User " + user + " has edited the article. " +
				  "This is no longer the latest version. " +
				  "Editing disabled.";
			    alert(msg);
			    var $msg = $( "<div class='alert alert-danger' >" +
					  msg + "</div>")
			    $("#grp-content-title").prepend($msg);
			}
		    },
		    error: function(data){
			console.log("Error: ", data);
		    }
		});
	    }, 15000);
	}
});
