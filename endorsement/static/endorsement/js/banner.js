// manage endorsemnt reason input
/* jshint esversion: 6 */

var Banner = (function () {
    return {
        renderMessages: function (messages) {
            var $banner = $('div.container.persistent-messages'),
                source,
                template;

            $.each(messages, function (level, messages) {
                var $level = $('div.alert-' + level),
                    unique_messages = [];

                $.each(messages, function () {
                    if ($('[data-message-hash="' + this.hash + '"]', $level).length === 0) {
                        unique_messages.push(this);
                    }
                });

                if (unique_messages.length) {
                    if ($level.length) {
                        source = $("#persistent-message").html();
                        template = Handlebars.compile(source);

                        $.each(unique_messages, function () {
                            $level.prepend(template(this));
                        });
                    } else {
                        source = $("#persistent-messages").html();
                        template = Handlebars.compile(source);

                        $banner.append(template({
                            message_level: level,
                            messages: unique_messages
                        }));
                    }
                }
            });
        },
        removeMessage: function (level, hash) {
            var $level = $('div.alert-' + level),
                $message = $('[data-message-hash="' + hash  + '"]', $level);

            if ($message.length) {
                $message.remove();
            }

            if ( $level.children().length === 0 ) {
                $level.remove();
            }
        }
    };
}());

export { Banner };
