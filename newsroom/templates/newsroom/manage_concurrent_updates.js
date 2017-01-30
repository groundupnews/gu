// Cookie code copied from Django documentation
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
	    var cookie = $.trim(cookies[i]);
	    // Does this cookie string begin with the name we want?
	    if (cookie.substring(0, name.length + 1) == (name + '=')) {
		cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		break;
	    }
        }
    }
    return cookieValue;
}

$(document).ready(function() {
    var editors_enabled = true;
    var form_original_data = $("#article_form").serialize();

    function checkFormChanged()
    {
        if (editors_enabled) {
            if ($("#article_form").serialize() != form_original_data) {
                return true;
            }
        }
        return false;
    }

    function manageConcurrentEditing()
    {
        $.ajax({
	    url: "{% url "article.concurrent_check" %}",
	    type:"POST",
	    headers: { "X-CSRFToken": getCookie("csrftoken") },
	    data: {
                "pk": {{pk}},
                "version": {{version}},
                "changed": checkFormChanged()
            },
	    dataType: 'json',
	    success: function(json){
	        edited_by = json["edited_by"];
	        if (edited_by != "(None)") {
		    clearTimeout(timerCheckConcurrency);
		    $("form :input").attr("readonly","readonly");
		    for(name in CKEDITOR.instances) {
		        CKEDITOR.instances[name].setReadOnly();
		    }
		    msg = "User " + edited_by +
		        " has edited the article. This is no longer " +
		        "the latest version. Editing disabled."
                    if (checkFormChanged() == true) {
		        alert(msg);
                    }
                    editors_enabled = false;
		    $("[id^=article_]").removeAttr('contenteditable').blur();
		    var $msg = $( "<div class='alert alert-danger' >" + msg +
			          "</div>");

		    if ($("#grp-content-title").length) {
		        $("#grp-content-title").prepend($msg);
		        $('input[type="submit"]').prop('disabled', true);
		    }
		    if ($("#article-content").length)
		        $("#article-content").prepend($msg);
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
                    if (checkFormChanged()) {
                        $("#admin-user").html("{{request.user}} (changed)");
                    }
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
    }, 10000);

    $('#saveedits').click(function(event){
        clearTimeout(timerCheckConcurrency);
    });


    save_clicked = false;
    $(window).bind("beforeunload", function() {
        if  (save_clicked == false) {
            if (checkFormChanged()) {
                return confirm("You have made changes. Do you really want to close?");
            }
        }
    });

    $("#article_form").submit(function() {
        clearTimeout(timerCheckConcurrency);
        save_clicked = true;
        return true;
    });

});
