// javascript for common notification engine

var Notify = {
    _queue: [],
    _bound: false,

    success: function (msg) {
        Notify._notify(msg, 'alert-success');
    },

    error: function (msg) {
        Notify._notify(msg, 'alert-danger', 7000);
    },

    warning: function (msg) {
        Notify._notify(msg, 'alert-warning');
    },

    _notify: function (msg, div_class, fade) {
        var launch = (Notify._queue.length === 0),
            msg_data = {msg: msg, div_class: div_class, fade: fade};

        if (!Notify._bound) {
            Notify._bound = true;
            $('body').on('notify:MessageDisplayed', function () {
                Notify._display();
            });
        }

        $.each(Notify._queue, function () {
            if (this.msg === msg) {
                msg_data = null;
                return false;
            }
        });

        if (msg_data) {
            Notify._queue.push(msg_data);
        }

        if (launch) {
            Notify._display();
        }
    },

    _display: function () {
        var $notify,
            msg,
            div_class,
            fade;

        if (Notify._queue.length) {
            msg = Notify._queue[0].msg;
            div_class = Notify._queue[0].div_class;
            fade = Notify._queue[0].fade;
        } else {
            return;
        }

        $notify = $('<div></div>')
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
                Notify._queue.shift();
                $('body').trigger('notify:MessageDisplayed');
            });
    }
};
