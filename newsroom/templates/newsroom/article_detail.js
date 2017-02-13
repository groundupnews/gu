{% load staticfiles %}

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

    $('#print-article').click(function(){
	$("aside").remove();
	var print_contents = getPureArticle();
	print_contents = "<style>body { margin: 50px; }" +
	                 "img { max-width:90%; }</style>" +
	                 print_contents;
        return_button = "<p><a href='{{request.build_asolute_uri}}'>Back</a></p>";
        document.body.innerHTML = print_contents;

	window.print();
        document.body.innerHTML = return_button + print_contents;
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


    CKEDITOR.instances.article_title.on('change', function()
	{
	    update_form("article_title",
			"id_title");
	});

    CKEDITOR.instances.article_subtitle.on('change', function()
	{
	    update_form("article_subtitle",
			"id_subtitle");
	});


    {% if article.cached_primary_image %}
    CKEDITOR.instances.article_primary_image_caption.on('change', function()
	{
	    update_form("article_primary_image_caption",
			"id_primary_image_caption");
	});
    {% endif %}

    CKEDITOR.instances.article_body.on('change', function()
	{
	    update_form("article_body",
			"id_body");
	});
    {% endif %}
});


{% if can_edit %}
{% include "newsroom/manage_concurrent_updates.js" with pk=article.pk version=article.version %}

{% endif %}
