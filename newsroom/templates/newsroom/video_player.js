/* Click-to-play YouTube embed. */

(function () {
    var player = document.querySelector("[data-video-player]");

    function play(seconds) {
        if (!player) {
            return;
        }
        var url = player.getAttribute("data-embed") + "&autoplay=1";
        if (seconds) {
            url += "&start=" + seconds;
        }
        var iframe = document.createElement("iframe");
        // YouTube blocks playback with "error 153" when no HTTP Referer reaches
        // it. The site sends Referrer-Policy: same-origin, which strips the
        // header on cross-origin requests, so this iframe opts itself back into
        // sending the origin. Set before src, or the request goes out first.
        iframe.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
        iframe.src = url;
        iframe.title = player.getAttribute("data-title") || "Video";
        iframe.setAttribute("allowfullscreen", "");
        iframe.setAttribute(
            "allow",
            "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share"
        );
        player.innerHTML = "";
        player.appendChild(iframe);
    }

    if (player) {
        var start = player.querySelector(".gu-video-player__start");
        if (start) {
            start.addEventListener("click", function (event) {
                event.preventDefault();
                play(0);
            });
        }
    }

    document.querySelectorAll("[data-video-seek]").forEach(function (button) {
        button.addEventListener("click", function () {
            play(parseInt(button.getAttribute("data-video-seek"), 10) || 0);
            if (player) {
                player.scrollIntoView({ behavior: "smooth", block: "center" });
            }
        });
    });

    // The Clip entries in the page's structured data point at #t=<seconds>,
    // so honour that on arrival.
    if (player) {
        var hash = window.location.hash.match(/^#t=(\d+)$/);
        if (hash) {
            play(parseInt(hash[1], 10));
        }
    }

    document.querySelectorAll("[data-copy-link]").forEach(function (link) {
        link.addEventListener("click", function (event) {
            if (!navigator.clipboard) {
                return;
            }
            event.preventDefault();
            navigator.clipboard.writeText(link.href).then(function () {
                link.title = "Link copied";
            });
        });
    });
})();
