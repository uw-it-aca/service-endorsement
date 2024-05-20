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
                fade,
                src = $('#notify_template').html(),
                template = Handlebars.compile(src),
                html = template({message: msg, notify_class: div_class});

            if (_queue.length) {
                msg = _queue[0].msg;
                div_class = _queue[0].div_class;
                fade = _queue[0].fade;
            } else {
                return;
            }

            $notify = $(html);
            $notify.appendTo($('body'));
            $notify
                .css('top', $('.tab.active').offset().top + 'px')
                .css('left', (($(document).width() - $notify.width())/2) + 'px')
                .fadeOut(fade || 3500, function () {
                    $(this).remove();
                    _queue.shift();
                    $('body').trigger('notify:MessageDisplayed');
                });
        };

    return {
        success: function (msg, fade=3500) {
            _notify(msg, 'alert-success', fade);
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
