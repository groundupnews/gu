{% load static %}

const id_prefix = "id_";
const article_prefix = "article_";
const view_prefix = "view_";
const deck_suffix = "_on_deck";

var admin_open = true;

function getPureArticle()
{
    let pure_article = "<h1>" +
        document.getElementById("article_title").textContent + "</h1>";
    if (document.getElementById("article_subtitle").length)
	pure_article += "<h2>" + document.getElementById("article_subtitle").textContent + "</h2>";

    pure_article += "<p>" + document.getElementById("article-byline").textContent + "</p>";
    pure_article += "<p>" + "{{ article.published|date:'j F Y'}}" + "</p>";
    if (document.getElementById("article-primary-image"))
	pure_article += document.getElementById("article-primary-image").innerHTML;
    pure_article += document.getElementById("article_body").innerHTML;
    return pure_article;
}

{% if can_edit %}

let edit_mode;

function charsAndWordsLength(str)
{
    return str.trim().length + "/" +
        str.trim().split(" ").filter(function(x) {
            return x.length > 0;
        }).length;
}

function showSave()
{
    document.getElementById("edit-menu-save").style.display = "inherit";
}

/* Receive the file url from the FileBrowser's FB_CKEditor.js
* (in static/newsroom/js) and remove the MEDIA URL from it.
*/
function receiveSummaryImage(url)
{
    document.getElementById("id_summary_image").value =
        decodeURI(url.substr("{{MEDIA_URL}}".length));
    showSave();
}

function getSummaryImage()
{
    return "{{MEDIA_URL}}" + encodeURI(document.getElementById("id_summary_image").value);
}

function receiveAudioSummary(url)
{
    document.getElementById("id_audio_summary").value =
        decodeURI(url.substr("{{MEDIA_URL}}".length));
    showSave();
}

function getAudioSummary()
{
    return "{{MEDIA_URL}}" + encodeURI(document.getElementById("id_audio_summary").value);
}
/* Works with ajax_select to receive data from a popup window in which an author was created.
   Sets first available author field with the new author. */
function receiveAuthor(author)
{
    const nums = ["01", "02", "03", "04", "05"]
    for (const num of nums) {
        const id = "id_author_" + num + "_on_deck";
        const author_div = document.getElementById(id);
        if (author_div.innerHTML === "") {
            $("#id_author_" + num).trigger('didAddPopup',[author.pk, author.name]);
            showSave();
            break;
        }
    }
}

/* Works with ajax_select to receive data from a popup window that
   created a lookup database entry.
*/
function receiveAjaxField(field, obj)
{
    const id = "id_" + field + "_on_deck";
    const div = document.getElementById(id);
    $("#id_" + field).trigger('didAddPopup',[obj.pk, obj.value]);
    showSave();
}

function updateStats() {
    document.getElementById("article__statistics").innerHTML =
        "Words: " + total_words(document.getElementById("article_body")) +
        "<br/>" +
        "Billable: " + billable_words(document.getElementById("article_body"));
}



function setupFormSubmit()
{
    document.getElementById("saveedits").addEventListener(
        "click", function(e) {
            if (document.getElementById("article_title").textContent == "") {
                alert("Title can't be blank");
                e.preventDefault();
                return;
            }
            // Move back input elements that were moved
            let form = document.getElementById("article_form");
            const inputElems = document.querySelectorAll('[data-type="input"]');
            for (let elem of inputElems) {
                if (! (elem in form.elements)) {
                    form.appendChild(elem);
                    if (elem.getAttribute('data-ajax') == 'y') {
                        let deck = document.
                            getElementById(elem.id.replace("_text", deck_suffix));
                        if (! (elem in form.elements)) form.appendChild(deck);
                    }
                }
            }

            // Copy contenteditables
            let elems = form.querySelectorAll('[data-type="contenteditable"]');
            if (edit_mode == false) {
                edit_mode = true;
                initializeEditors();
            }
            for (let elem of elems) {
                const copyFromId = elem.id.replace(id_prefix, article_prefix);
                if (elem.getAttribute('data-editor')) {
                    if (copyFromId in CKEDITOR.instances) {
                        elem.value = CKEDITOR.instances[copyFromId].getData();
                    }
                } else {
                    const copyFrom = document.getElementById(copyFromId);
                    if (copyFrom) elem.value = copyFrom.innerHTML;
                }
            }
            document.getElementById('article_title').innerHTML =
                document.getElementById('article_title').innerHTML.
                replace(/<\/?[^>]+(>|$)/g, "").trim();

            // Move back tweets
            // const tweets = document.getElementById('tweet_formset');
            // form.appendChild(tweets);

            // Move back republishers
            const republishers = document.getElementById('republisher_formset');
            form.appendChild(republishers);

            // Move back corrections
            const corrections = document.getElementById('correction_formset');
            form.appendChild(corrections);
            document.body.style.cursor = 'wait';
        });
}

function setupAdminPanel()
{
    $("#admin-toggle").click(function() {
        if (admin_open) {
            document.getElementById('admin-area').style.height = "20px";
            document.getElementById('admin-area').style.width = "20px";
        } else {
            document.getElementById('admin-area').style.height = "inherit";
            document.getElementById('admin-area').style.width = "inherit";
        }
        admin_open = !admin_open;
    });
    updateStats();
}

function setupButtons()
{
    let buttons = document.getElementsByClassName('button-action');
    for (let btn of buttons) {
        let realBtn = document.getElementById(btn.id.substr(3));
        if (realBtn) {
            realBtn.addEventListener('click', function() {
                btn.value = 'y';
                document.getElementById("saveedits").click();
            });
        }
    }
}

function initializeEditors()
{
    const contentEditables = document.querySelectorAll(
        '[data-type="contenteditable"]');

    for (let elem of contentEditables) {
        let id = elem.id.replace(id_prefix, article_prefix);
        if (elem.getAttribute("data-editor")) {
            const base = "{% static 'newsroom/js/' %}";
            const config = base + elem.getAttribute("data-editor");

            if (document.getElementById(id)) {
                CKEDITOR.inline(id, {
                    customConfig: config
                });
            }
        }
    }

    for(const instance in CKEDITOR.instances) {
        CKEDITOR.instances[instance].on('change', function() {
            showSave();
        });
    }
    CKEDITOR.instances['article_body'].on('change', function() {
        updateStats();
    });
}

function setupNonCkeEditables()
{
    const contentEditables = document.querySelectorAll(
        '[data-type="contenteditable"]');

    for (let elem of contentEditables) {
        if (!elem.getAttribute("data-editor")) {
            let id = elem.id.replace(id_prefix, article_prefix);
            if (document.getElementById(id)) {
                document.getElementById(id).
                    setAttribute('title', elem.getAttribute('placeholder'));
                document.getElementById(id).addEventListener('input', function() {
                    showSave();
                });
            }
        }
    }
}

function copyForm() {
    const contentEditables = document.querySelectorAll(
        '[data-type="contenteditable"]');
    for (let elem of contentEditables) {
        let id = elem.id.replace(id_prefix, article_prefix);
        if (document.getElementById(id)) {
            document.getElementById(id).innerHTML =
                elem.value;
        }
    }
    updateStats();
}



function setupInputFields()
{
    let form = document.getElementById("article_form");
    // Move input fields
    const elems = form.querySelectorAll('[data-type="input"]');
    for (let elem of elems) {
        elem.addEventListener(
            'input', function() {
                showSave();
            });
        const id = elem.id.replace(id_prefix, view_prefix);
        let viewElem = document.getElementById(id);
        if (viewElem) {
            if (!viewElem.getAttribute('title')) {
                viewElem.setAttribute('title', elem.getAttribute('placeholder'));
            }
            viewElem.appendChild(elem);
            if (elem.getAttribute('data-ajax') == "y") {
                let deckElem = document.getElementById(
                    elem.id.replace("_text", deck_suffix));
                if (deckElem) viewElem.appendChild(deckElem);
            }
        }
    }

    // Enable save if trash icon clicked
    const trash_icons = document.getElementsByClassName('ui-icon-trash');
    for (let trash of trash_icons) {
        trash.addEventListener('click', function() {
            showSave();
        });
    }


    // Specific field processing
    const d = new Date();
    flatpickr("#id_published", {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        time_24hr: true,
        defaultHour:
        {% if article.published %}
        '{{article.published|date:"H"}}'
        {% else %}
        d.getHours()
        {% endif %},
        defaultMinute:
        {% if article.published %}
        '{{article.published|date:"i"}}'
        {% else %}
        d.getMinutes()
        {% endif %},
        onChange: function(selectedDates, dateStr, instance) {
            showSave();
        },
    });


    if (document.getElementById("new-author")) {
        document.getElementById("new-author").
            addEventListener('click', function() {
                window.open("{% url 'newsroom:author.add' %}",
                            "author.add_window",
                            "popup=1,left=100,top=100");
            });
    }

    if (document.getElementById("new-topic")) {
        document.getElementById("new-topic").
            addEventListener('click', function() {
                window.open("{% url 'newsroom:topic_create' %}",
                            "topic_create_window",
                            "popup=1,left=100,top=100");
            });
    }

    if (document.getElementById("select-file")) {
        document.getElementById("select-file").
            addEventListener('click', function() {
                window.open("/admin/filebrowser/browse/?pop=3&summary=1&dir=images",
                            "select_file_win",
                            "popup=1,left=100,top=100");
            });
    }
    if (document.getElementById("select-audio")) {
        document.getElementById("select-audio").
            addEventListener('click', function() {
                window.open("/admin/filebrowser/browse/?pop=3&audio=1&dir=sound/summaries",
                            "select_audio_win",
                            "popup=1,left=100,top=100");
            });
    }
    if (document.getElementById("new-twit")) {
        document.getElementById("new-twit").
            addEventListener('click', function() {
                window.open("{% url 'socialmedia:twitterhandle.add' %}",
                            "twit_new_win",
                            "popup=1,left=100,top=100");
            });
    }


    document.getElementById('headline_len').textContent =
        charsAndWordsLength(document.getElementById('article_title').textContent);
    document.getElementById('article_title').addEventListener(
        'input', function(e) {
            document.getElementById('headline_len').textContent =
                charsAndWordsLength(e.target.textContent);
        });
}

// function setupTweets()
// {
//    const view_tweets = document.getElementById('view_tweets')
//    const tweets = document.getElementById('tweet_formset');
//    view_tweets.appendChild(tweets);
//    view_tweets.addEventListener('input', function() {
//        showSave();
//    });
// }

function setupCorrections()
{
    const view_corrections = document.getElementById('view_corrections')
    const corrections = document.getElementById('correction_formset');
    view_corrections.appendChild(corrections);
    view_corrections.addEventListener('input', function() {
        showSave();
    });
}

function setupRepublishers()
{
    const view_republishers = document.getElementById('view_republishers')
    const republishers = document.getElementById('republisher_formset');
    view_republishers.appendChild(republishers);
    view_republishers.addEventListener('input', function() {
        showSave();
    });
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
            elem.classList.add('edit-on');
            if (elem.style.display == "none") {
                elem.style.display = "inherit";
            }
        } else {
            elem.contentEditable = 'false';
            elem.classList.remove('edit-on');
            if (elem.textContent.trim() == "") {
                elem.style.display = "none";
            }
        }
    }
    if (edit_mode) {
        initializeEditors();
    } else {
        destroyEditors();
    }
    elems = document.querySelectorAll('[data-type="input"]');

    for (let elem of elems) {
        if (edit_mode) {
            elem.style.display = elem.getAttribute("data-display") ||  "inherit";
            if (elem.getAttribute('data-ajax') == 'y') {
                let deckElem = document.getElementById(
                    elem.id.replace("_text", deck_suffix));
                if (deckElem) deckElem.style.display = "inline-block";
            }
            elem.classList.add('edit-on');
        } else {
            elem.style.display = "none";
            if (elem.getAttribute('data-ajax') == 'y') {
                let deckElem = document.getElementById(
                    elem.id.replace("_text", deck_suffix));
                if (deckElem) deckElem.style.display = "none";
            }
            elem.classList.remove('edit-on');
        }
    }

    elems = document.getElementsByClassName('edit-only');
    for (let elem of elems) {
        if (edit_mode) {
            elem.style.display = elem.getAttribute("data-display") || "inherit";
        } else {
            elem.style.display = "none";
        }
    }
}

function toggleEditables(elem)
{
    edit_mode = !edit_mode;
    if (edit_mode)
        elem.textContent = "View";
    else
        elem.textContent = "Edit";
    setEditables();
}

{% endif %}

function shareButtons()
{
    $('#twitter-share').click(function(){
	var article_title =
            encodeURI('{{article.title|addslashes|linebreaksbr|safe}}').
            substring(0, 115);
	var url = encodeURI('{{ request.build_absolute_uri }}');
	var twitter_url = "https://twitter.com/intent/tweet?text=" +
	                  article_title + "&url=" + url;
	var win = window.open(
            twitter_url,
            "_blank",
            "toolbar=no, scrollbars=yes, resizable=yes, top=20%, left=340, width=400, height=400");
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
	const subject = encodeURI(
            '{{article.title|addslashes|linebreaksbr|safe}}');
	const body = encodeURI(
            '{{article.cached_summary_text|addslashes|striptags|truncatewords:100|safe}}'
                + ' ' +	'{{ request.build_absolute_uri }}');
	const mail_url = "mailto:?subject=" + subject + "&body=" + body;
	const win = window.open(mail_url, '_self');
	win.focus();
	return false;
    });
}

jQuery(document).ready(function ($) {

    shareButtons();

    {% if can_edit %}
    edit_mode = false;
    const urlParams = new URLSearchParams(window.location.search);
    if(urlParams.get('edit') === "y")
        toggleEditables(document.getElementById("edit-toggle"));
    if ({{from_form}}) edit_mode = true;
    setupAdminPanel();
    setupButtons();
    setupFormSubmit();
    if ({{from_form}}) {
        copyForm();
    }
    setupNonCkeEditables();
    setupInputFields();
    // setupTweets();
    setupRepublishers();
    setupCorrections();
    setEditables();
    {% endif %}
});


{% if can_edit %}
{% include "newsroom/manage_concurrent_updates.js" with pk=article.pk version=article.version %}
{% endif %}
