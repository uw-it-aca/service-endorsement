// javascript for common notification engine

var Notify = {
    success: function (msg) {
        Notify._notify(msg, 'alert-success')
    },

    error: function (msg) {
        Notify._notify(msg, 'alert-danger', 7000)
    },

    warning: function (msg) {
        Notify._notify(msg, 'alert-warning')
    },

    _notify: function (msg, div_class, fade) {
        var $notify = $('<div></div>')
            .html(msg)
            .addClass(div_class)
            .appendTo($('body'));

        $notify
            .css('display', 'block')
            .css('position', 'absolute')
            .css('padding', '6px')
            .css('border-radius', '3px')
            .css('top', $(document).scrollTop())
            .css('left', (($(document).width() - $notify.width())/2) + 'px')
            .fadeOut(fade || 3500, function () {
                $(this).remove();
            });
    }
};
