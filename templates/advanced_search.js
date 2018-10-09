$( document ).ready(function() {
    var search_input = $('.header__search__input')
    var advanced_search = $('.advanced-search')
    var header_bar = $('.header')
    var adv_arrow = $('.adv-filter-arrow')
    var adv_form = $('.adv-filter-form')

    if ($(window).width() > 768) {
        search_input.on('focus', function() {
            advanced_search.slideDown('slow')
        })
        header_bar.on('mouseleave', function() {
            advanced_search.slideUp('slow')
        })
    }
        
    adv_arrow.on('click', function() {
        var icon = $(this)
        if (icon.hasClass('fa-angle-up')) {
            adv_form.slideUp('slow')
            adv_arrow.toggleClass('fa-angle-up fa-angle-down')
        } else {
            $('.adv-filter-form').slideDown('slow')
            adv_arrow.toggleClass('fa-angle-down fa-angle-up')
        }
    })

    $('[data-toggle="datepicker"]').datepicker({
        format: 'dd/mm/yyyy',
    });
});
