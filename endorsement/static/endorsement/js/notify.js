// javascript for common notification engine
/* jshint esversion: 6 */

var Notify = (function () {
    var _queue = [],
        _bound = false,
        _notify = function (msg, div_class, fade) {
            var launch = (_queue.length === 0),
                msg_data = {msg: msg, div_class: div_class, fade: fade};

            if (!_bound) {
                _bound = true;
                $('body').on('notify:MessageDisplayed', function () {
                    _display();
                });
            }

            $.each(_queue, function () {
                if (this.msg === msg) {
                    msg_data = null;
                    return false;
                }
            });

            if (msg_data) {
                _queue.push(msg_data);
            }

            if (launch) {
                _display();
            }
        },
        _display = function () {
            var $notify,
                msg,
                div_class,
                fade;

            if (_queue.length) {
                msg = _queue[0].msg;
                div_class = _queue[0].div_class;
                fade = _queue[0].fade;
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
                    _queue.shift();
                    $('body').trigger('notify:MessageDisplayed');
                });
        };

    return {
        success: function (msg) {
            _notify(msg, 'alert-success');
        },

        error: function (msg) {
            _notify(msg, 'alert-danger', 7000);
        },

        warning: function (msg) {
            _notify(msg, 'alert-warning');
        },
    };
}());

export { Notify };
