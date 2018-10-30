$( document ).ready(function() {
    var search_input = $('.header__search__input')
    var search_button = $('.header__search-button')
    var advanced_search = $('.advanced-search')
    var advanced_search_input = $('#id_adv_search')
    var advanced_search_button = $('.adv-filter-submit')
    var header_bar = $('.header')
    var adv_arrow = $('.adv-filter-arrow')
    var adv_form = $('.adv-filter-form')

    if ($(window).width() > 1024) {
        header_bar.on('mouseenter', function() {
            advanced_search.slideDown('slow')
        })
        $('#BelowTheBanner').on('mouseenter', function() {
            advanced_search.slideUp('slow')
        })
    }

    if (search_input.val() !== undefined && search_input.val().trim() === "") {
        search_button.prop('disabled', true)
    }

    search_input.on('keyup paste change input', function() {
        var input = $(this)
        if (input.val().trim() === "") {
            search_button.prop('disabled', true)
        } else {
            search_button.prop('disabled', false)
        }
    })

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
