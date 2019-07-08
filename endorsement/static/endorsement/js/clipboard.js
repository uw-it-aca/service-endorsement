// javascript handling clipboard copying
/* jshint esversion: 6 */

var ClipboardCopy = (function () {
    var _registerEvents = function () {
        $(document).on('click', '[data-clipboard]', function (e) {
            ClipboardCopy._copy_clipboard($(this));
        });
    },

    _copy_clipboard = function ($node) {
        var url = $node.attr('data-clipboard'),
            msg = $node.attr('data-clipboard-msg'),
            $txt;

        $txt = $('<input>')
            .css('position', 'absolute')
            .css('left', '-2000px')
            .val(url)
            .appendTo(document.body);
        $txt.select();
        document.execCommand('copy');
        $txt.remove();
        Notify.success(msg);
    };

    return {
        load: function () {
            _registerEvents();
        }
    };
}());

export { ClipboardCopy };
