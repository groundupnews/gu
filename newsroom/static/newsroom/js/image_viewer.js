// Opens article images over the page instead of the huge original in a new tab
(function () {
    'use strict';

    var body = document.getElementById('article_body');
    if (!body || typeof HTMLDialogElement !== 'function') {
        return;
    }
    var links = body.querySelectorAll('a.bigger-image');
    if (!links.length) {
        return;
    }

    var dialog, viewerImg, captionEl, originalLink, lastLink;
    var loadToken = 0;

    function enlargedUrl(href) {
        var path = new URL(href, window.location.href).pathname;
        return '/image/enlarged/?src=' + encodeURIComponent(path);
    }

    function captionFor(link) {
        var figure = link.closest('figure');
        var figcaption = figure && figure.querySelector('figcaption');
        if (figcaption) {
            return figcaption.textContent.trim();
        }
        var next = link.parentElement && link.parentElement.nextElementSibling;
        if (next && next.classList.contains('caption')) {
            return next.textContent.trim();
        }
        return '';
    }

    function build() {
        dialog = document.createElement('dialog');
        dialog.className = 'gu-viewer';
        dialog.setAttribute('aria-label', 'Enlarged image');
        dialog.innerHTML =
            '<div class="gu-viewer__bar">' +
                '<a class="gu-viewer__original" target="_blank" rel="noopener">Open original</a>' +
                '<button type="button" class="gu-viewer__close" aria-label="Close" autofocus>' +
                    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
                        '<path d="M6 6l12 12M18 6L6 18"/>' +
                    '</svg>' +
                '</button>' +
            '</div>' +
            '<div class="gu-viewer__stage"><img class="gu-viewer__img" alt=""></div>' +
            '<p class="gu-viewer__caption"></p>';
        document.body.appendChild(dialog);

        viewerImg = dialog.querySelector('.gu-viewer__img');
        captionEl = dialog.querySelector('.gu-viewer__caption');
        originalLink = dialog.querySelector('.gu-viewer__original');

        dialog.querySelector('.gu-viewer__close').addEventListener('click', function () {
            dialog.close();
        });
        // tap outside the image to close
        dialog.addEventListener('click', function (e) {
            if (e.target === dialog || e.target.classList.contains('gu-viewer__stage')) {
                dialog.close();
            }
        });
        dialog.addEventListener('close', function () {
            loadToken++;
            document.documentElement.classList.remove('gu-viewer-open');
            viewerImg.removeAttribute('src');
            if (lastLink) {
                lastLink.focus({ preventScroll: true });
            }
        });
    }

    function open(link) {
        if (!dialog) {
            build();
        }
        var thumb = link.querySelector('img');
        var token = ++loadToken;

        viewerImg.src = thumb.currentSrc || thumb.src;
        viewerImg.alt = thumb.alt || '';
        captionEl.textContent = captionFor(link);
        captionEl.hidden = !captionEl.textContent;
        originalLink.href = link.href;
        dialog.classList.add('is-loading');
        document.documentElement.classList.add('gu-viewer-open');
        dialog.showModal();

        var big = new Image();
        big.onload = function () {
            var swap = function () {
                if (token === loadToken) {
                    viewerImg.src = big.src;
                    dialog.classList.remove('is-loading');
                }
            };
            // decode first so the swap doesn't stutter
            if (big.decode) {
                big.decode().then(swap, swap);
            } else {
                swap();
            }
        };
        big.onerror = function () {
            if (token === loadToken) {
                dialog.classList.remove('is-loading');
            }
        };
        big.src = enlargedUrl(link.href);
    }

    Array.prototype.forEach.call(links, function (link) {
        var thumb = link.querySelector('img');
        if (!thumb) {
            return;
        }
        link.setAttribute('aria-label',
            'Enlarge image' + (thumb.alt ? ': ' + thumb.alt : ''));
        link.addEventListener('click', function (e) {
            // ctrl/cmd-click still opens a new tab
            if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
                return;
            }
            e.preventDefault();
            lastLink = link;
            open(link);
        });
    });
})();
