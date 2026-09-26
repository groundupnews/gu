(function () {
    document.querySelectorAll('[data-video-block]').forEach(function (block) {
        var rail = block.querySelector('.gu-video-block__rail');
        var controls = block.querySelector('.gu-video-block__controls');
        var previous = controls.querySelector('[data-video-direction="-1"]');
        var next = controls.querySelector('[data-video-direction="1"]');
        function update() {
            var end = rail.scrollWidth - rail.clientWidth;
            controls.hidden = end <= 1;
            previous.disabled = rail.scrollLeft <= 1;
            next.disabled = rail.scrollLeft >= end - 1;
        }
        controls.addEventListener('click', function (event) {
            var button = event.target.closest('button');
            if (!button || button.disabled) return;
            var card = rail.querySelector('.gu-video-block__card');
            var step = card.getBoundingClientRect().width + parseFloat(getComputedStyle(rail).gap);
            rail.scrollBy({
                left: Number(button.dataset.videoDirection) * step,
                behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
            });
        });
        rail.addEventListener('scroll', update, { passive: true });
        if (window.ResizeObserver) new ResizeObserver(update).observe(rail);
        else window.addEventListener('resize', update);
        update();
    });
})();
