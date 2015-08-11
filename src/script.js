$(function() {
    $('.overlay').click(function() {
        $('.overlay').addClass('overlay--hidden');
        $('.player__popup').addClass('player__popup--hidden');
    });

    $('.player img').click(function() {
        $('.player__popup').addClass('player__popup--hidden');
        $(this).siblings('.player__popup').removeClass('player__popup--hidden');
        $(this).siblings('.overlay').removeClass('overlay--hidden');
    });
});
