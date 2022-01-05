{% load static %}

function getPureArticle()
{
    var pure_article = "<h1>" + $("#article_title").text() + "</h1>";
    if ($("#article_subtitle").length)
	pure_article += "<h2>" + $("#article_subtitle").text() + "</h2>";
    if ($(".article-byline").length) {
	pure_article += "<p>" + $(".article-byline").text() + "</p>";
    }
    if ($(".article-dateline").length)
	pure_article += "<p>" + $(".article-dateline").text() + "</p>";
    if ($("#article-primary-image").length)
	pure_article += $("#article-primary-image").html();
    pure_article += $("#article_body").html();
    return pure_article;
}


{% if can_edit %}

var edit_mode = false;

function initializeEditors()
{
    function update_form(editor, field) {
	document.getElementById(field).value =
	    CKEDITOR.instances[editor].getData();
    }

    CKEDITOR.inline( 'article_title', {
	customConfig: "{% static 'newsroom/js/ck_inline_plaintext_config.js' %}"
    });
    CKEDITOR.inline( 'article_subtitle', {
	customConfig: "{% static 'newsroom/js/ck_inline_basic_config.js' %}"
    });
    {% if article.cached_primary_image %}
    CKEDITOR.inline( 'article_primary_image_caption', {
	customConfig: "{% static 'newsroom/js/ck_inline_basic_config.js' %}"
    });
    {% endif %}

    CKEDITOR.inline( 'article_body', {
	customConfig: "{% static 'newsroom/js/ck_inline_config.js' %}"
    });

    for(const instance in CKEDITOR.instances) {
        CKEDITOR.instances[instance].on('change', function() {
            document.getElementById("edit-menu-save").style.display = "inherit";
            let id = instance.replace("article_", "id_");
            update_form(instance, id);
        });
    }
}

function destroyEditors()
{
    for(const instance in CKEDITOR.instances)
        CKEDITOR.instances[instance].destroy();
}

function setEditables()
{
    let elems = document.getElementsByClassName("editable");
    for (let elem of elems) {
        if (edit_mode) {
            elem.contentEditable = 'true';
            if (elem.style.display == "none") {
                elem.style.display = "inherit";
            }
            elem.classList.add('edit-on');
        } else {
            destroyEditors();
            elem.contentEditable = 'false';
            if (elem.textContent.trim() == "") {
                elem.style.display = "none";
            }
            elem.classList.remove('edit-on');
        }
    }
    if (edit_mode) initializeEditors();
}

function toggleEditables(elem)
{
    edit_mode = !edit_mode;
    if (edit_mode)
        elem.textContent = "Edit off";
    else
        elem.textContent = "Edit on";
    setEditables();
}

{% endif %}

jQuery(document).ready(function ($) {

    $('#twitter-share').click(function(){
	var article_title = encodeURI('{{article.title|addslashes|linebreaksbr|safe}}').
	                                                                          substring(0, 115);
	var url = encodeURI('{{ request.build_absolute_uri }}');
	var twitter_url = "https://twitter.com/intent/tweet?text=" +
	                  article_title + "&url=" + url;
	var win = window.open(twitter_url, "_blank", "toolbar=no, scrollbars=yes, resizable=yes, top=20%, left=340, width=400, height=400");
	win.focus();
	return false;
    });
    $('#facebook-share').click(function(){
	var url = encodeURI('{{ request.build_absolute_uri }}');
	var facebook_url = "https://www.facebook.com/sharer/sharer.php?u=" + url;
	var win = window.open(facebook_url, "_blank", "toolbar=no, scrollbars=yes, resizable=yes, top=20%, left=340, width=550, height=400");
	win.focus();
	return false;
    });
    $('#whatsapp-share').click(function(){
	var whatsapp_url = 'whatsapp://send?text=' +
	                   encodeURI('{{ request.build_absolute_uri }}');
	var win = window.open(whatsapp_url, '_blank');
	win.focus();
	return false;
    });
    $('#email-share').click(function(){
	var subject = encodeURI('{{article.title|addslashes|linebreaksbr|safe}}');
	var body = encodeURI('{{article.cached_summary_text|addslashes|striptags|truncatewords:100|safe}}' + ' ' +
			     '{{ request.build_absolute_uri }}');
	var mail_url = "mailto:?subject=" + subject + "&body=" + body;
	var win = window.open(mail_url, '_self');
	win.focus();
	return false;
    });

    {% if can_edit %}

    var content_div = $('#content-main');

    $("#publish-now" ).click(function() {
	$("#input-is-published").val("Now");
	$("#saveedits").click();
	return false;
    });

    $("#make-unsticky" ).click(function() {
	$("#input-unsticky").val("YES");
	$("#saveedits").click();
	return false;
    });


    $("#make-top-story" ).click(function() {
	$("#input-top-story").val("YES");
	$("#saveedits").click();
	return false;
    });

/*    $('#article_form').on('submit', function(e){

        e.preventDefault();

        $.ajax({
            type : "POST",
            url: "{% url 'newsroom:article.detail' article.slug %}",
            data: {
                document.getElementById(article_form).serialize();
                csrfmiddlewaretoken: '{{ csrf_token }}',
                dataType: "json",
            },

            success: function(data){
                $('#output').html(data.msg)
            },

            failure: function() {
                alert("Failure!");
            }
        });


    });
*/
    {% endif %}
});


{% if can_edit %}
{% include "newsroom/manage_concurrent_updates.js" with pk=article.pk version=article.version %}

{% endif %}
