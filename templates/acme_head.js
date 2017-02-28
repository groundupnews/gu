var googletag = googletag || {};
googletag.cmd = googletag.cmd || [];
googletag.cmd.push(function() {
    var mappings = googletag.sizeMapping().
        addSize([768, 0], [728, 90]).
        addSize([320, 0], [300, 250]).
        addSize([0, 0], [88, 31]).
        build();

    googletag.defineSlot('/49076269/acme_groundup_300_250',
                         [300, 250],
                         'div-gpt-ad-1488136564093-0').
	addService(googletag.pubads());

    googletag.defineSlot('/49076269/acme_ground_up_728_90',
                         [300, 250],
                         'div-gpt-ad-1488136619122-0').
        defineSizeMapping(mappings).
        addService(googletag.pubads());

    googletag.pubads().enableSingleRequest();
    googletag.enableServices();
});
