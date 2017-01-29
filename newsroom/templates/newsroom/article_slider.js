$(document).ready(function() {
    var pgwSlider = $('.pgwSlider').pgwSlider();
    pgwSlider.reload({
	displayControls : true,
	displayList: false,
	intervalDuration: 6000
    });
});
