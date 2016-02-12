// Cookie code copied from Django documentation
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
	    var cookie = jQuery.trim(cookies[i]);
	    // Does this cookie string begin with the name we want?
	    if (cookie.substring(0, name.length + 1) == (name + '=')) {
		cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		break;
	    }
        }
    }
    return cookieValue;
}

function manageConcurrentEditing()
{
    $.ajax({
	url: "{% url "article.concurrent_check" %}",
	type:"POST",
	headers: { "X-CSRFToken": getCookie("csrftoken") },
	data: { "pk": {{pk}}, "version": {{version}} },
	dataType: 'json',
	success: function(json){
	    edited_by = json["edited_by"];
	    if (edited_by != "(None)") {
		clearTimeout(timerCheckConcurrency);
		msg = "User " + edited_by +
		    " has edited the article. This is no longer " +
		    "the latest version. Editing disabled."
		alert(msg);
		$("form :input").attr("readonly","readonly");
		for(name in CKEDITOR.instances) {
		    CKEDITOR.instances[name].setReadOnly();
		}
		$("[id^=article_]").removeAttr('contenteditable').blur();
		var $msg = $( "<div class='alert alert-danger' >" + msg +
			      "</div>");

		if ($("#grp-content-title").length) {
		    $("#grp-content-title").prepend($msg);
		    $('input[type="submit"]').prop('disabled', true);
		}
		if ($("#content-main").length)
		    $("#content-main").prepend($msg);
	    }
	    if ($("#editing-article").length) {
		num_users = json["users"].length;
		var editor_html = "";
		for (var i = 0; i < num_users; ++i) {
		    editor_html += "<span class='editing-user'>" +
			json["users"][i] +
			"</span>";
		}
		$("#editing-article").html(editor_html);
	    }
	},
	error: function(data){
	    console.log("Error: ", data);
	}
    });
}

manageConcurrentEditing();

timerCheckConcurrency = window.setInterval(function(){
    manageConcurrentEditing();
}, 5000);
