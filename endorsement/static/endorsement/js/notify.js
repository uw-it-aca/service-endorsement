// javascript for common notification engine


var notify = function (msg) {
    var $notify = $('<div></div>')
        .html(msg)
        .addClass('alert-success')
        .appendTo($('body'));

    $notify
        .css('display', 'block')
        .css('position', 'absolute')
        .css('padding', '6px')
        .css('border-radius', '3px')
        .css('top', $(document).scrollTop())
        .css('left', (($(document).width() - $notify.width())/2) + 'px')
        .fadeOut(3500, function () {
            $(this).remove();
        });
};
