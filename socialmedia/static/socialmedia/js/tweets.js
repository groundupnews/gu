TIME_BETWEEN_TWEETS = 90;

function calc_tweet_chars(item) {
    var num_chars = $("#id_tweet_set-" + item + "-tweet_text").val().length;
    if ($("#id_tweet_set-" + item + "-image").val().length > 0) {
	num_chars += 24;
    }
    // Now for all the tags
    var tag_length = 0;

    var selector = "#tweet_set" + item + " .tag_accounts ul li";
    console.log("D0: ", $(selector).length);
    $(selector).each(function(i) {
	var s = $(this).text().trim();
        if (s.length > 0) {
            tag_length += s.length + 2;
        }
    });

    num_chars = 140 - num_chars - tag_length - 24;

    $("#tweet_set" + item + " .characters_left div").text(num_chars.toString());
    if (num_chars < 0) {
	$("#tweet_set" + item + " .characters_left div").css("color", "red");
    } else {
	$("#tweet_set" + item + " .characters_left div").css("color", "inherit");
    }
}

function createCallback( s ){
  return function() {
      calc_tweet_chars(s);
  }
}

// Appended to automatically generated tweets to make them unique
tweet_suffixes = [
    ".",
    ":",
    " :",
    " |",
    "|",
    "  |",
    " -",
    " —",
    "-",
    "--",
    "---",
    " --",
    ": -",
    ". -",
    " >",
    "  >",
    ". >",
    " >-",
    " *",
    " ·"
];

/* Executed when button to automatically generate tweets is clicked. */
function generate_tweets()
{
    var tweet_text = $("#id_title").val().trim();
    var image_link = "";
    var start_index = -1;
    var wait_time = 0;

    if (tweet_text.length == 0)
	return;
    var num_tweets = $("#tweet_set-group div.grp-tbody").length - 1;
    // Find first blank tweet
    for (var i = 0; i < num_tweets; ++i) {
	s = i.toString();
	if ($("#id_tweet_set-" + s + "-wait_time").val().trim().length > 0) {
	    wait_time = Number($("#id_tweet_set-" + s + "-wait_time").val())
		+ TIME_BETWEEN_TWEETS;
	    text = $("#id_tweet_set-" + s + "-tweet_text").val().trim();
	    if (text.length > 0) {
		tweet_text = text;
		image_link = $("#id_tweet_set-" + s + "-image").val().trim();
	    }
	} else {
	    start_index = i;
	    break;
	}
    }

    if (start_index >= 0) {
	var j = 0;
	for (var i = start_index; i < num_tweets && j < tweet_suffixes.length;
	     ++i, ++j) {
	    var s = i.toString();
	    var selector = $("#id_tweet_set-" + s + "-tweet_text");
	    if (selector.val().trim().length == 0)
		$(selector).val(tweet_text + tweet_suffixes[j]);
	    selector = $("#id_tweet_set-" + s + "-image");
	    if (selector.val().trim().length == 0)
		$(selector).val(image_link);

	    selector = $("#id_tweet_set-" + s + "-wait_time");
	    if (selector.val().trim().length == 0) {
		$(selector).val(wait_time.toString());
		wait_time = wait_time + TIME_BETWEEN_TWEETS;
	    }
	    else {
		wait_time = Number(selector.val()) +
		    TIME_BETWEEN_TWEETS;
	    }
	    calc_tweet_chars(s);
	}
    }
}


$(window).load(function() {
    /* Hook all entries to tweet length counter. */
    var num_entries = $("#tweet_set-group div.grp-tbody").length - 1;

    for (var i = 0; i < num_entries; ++i) {
	var s = i.toString();
	$("#id_tweet_set-" + s + "-tweet_text").on('input propertychange paste',
						   createCallback( s ));
	$("#id_tweet_set-" + s + "-image").on('input propertychange paste',
					      createCallback( s ));
	$("#s2id_id_tweet_set-" + s + "-tag_accounts ul").focusout(createCallback( s ));

    }

    // Hook "+" button that adds more rows to the tweet counter
    var target = document.querySelector('#tweet_set-group div.grp-table');
    var observer = new MutationObserver(function(mutations) {
	mutations.forEach(function(mutation) {
	    var s = ($("#tweet_set-group div.grp-tbody").length - 2).toString();
	    $("#id_tweet_set-" + s + "-tweet_text").on('input propertychange paste', function() {
		calc_tweet_chars(s);
	    });
	    $("#id_tweet_set-" + s + "-image").on('input propertychange paste', function() {
		calc_tweet_chars(s);
	    });
	    $("#s2id_id_tweet_set-" + s + "-tag_accounts ul").focusout(function() {
		calc_tweet_chars(s);
	    });
	});
    });

    var config = { attributes: false, childList: true, characterData: false };
    observer.observe(target, config);


    $("#tweet_set-group div.grp-row").
	append("|&nbsp;<a href='#' id='generate_tweets'><strong>Generate tweets</strong></a>");

    $("#tweet_set-group div.grp-row").
	on("click", "#generate_tweets",
	   function()
	   {
	       generate_tweets();
	       return false;
	   });

//    $("#tweet_set-group h2.grp-collapse-handler").click(
    $("#tweet_set-group").mouseenter(
	function() {
	    var num_tweets = $("#tweet_set-group div.grp-tbody").length - 2;
	    for (var i = 0; i < num_tweets; ++i) {
		calc_tweet_chars(i.toString());
	    }
	}
    );
});
