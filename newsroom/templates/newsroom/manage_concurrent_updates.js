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

timerCheckConcurrency = window.setInterval(function(){
    $.ajax({
	url: "{% url "article.concurrent_check" %}",
	type:"POST",
	headers: { "X-CSRFToken": getCookie("csrftoken") },
	data: { "pk": {{pk}}, "version": {{version}} },
	success: function(user){
	    if (user != "(None)") {
		clearTimeout(timerCheckConcurrency);
		msg = "User " + user +
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
	},
	error: function(data){
	    console.log("Error: ", data);
	}
    });
}, 10000);
