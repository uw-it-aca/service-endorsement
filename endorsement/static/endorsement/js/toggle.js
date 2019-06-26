// support toggle of hisden div
/* jshint esversion: 6 */

var TogglePanel = (function () {
    var _registerEvents = function () {
        $(document).on('click', '.panel-toggle', function (e) {
            var $link = $(this),
                $div = $link.next(),
                $panel = $link.closest('.panel');

            if ($div.hasClass('visually-hidden')) {
                $link.html($link.attr('data-conceal-text'));
                $div.removeClass('visually-hidden');
                $panel.trigger('endorse:PanelToggleExposed', [$div]);
            } else {
                $link.html($link.attr('data-reveal-text'));
                $div.addClass('visually-hidden');
                $panel.trigger('endorse:PanelToggleHidden', [$div]);
            }
        });
    };

    return {
        load: function () {
            _registerEvents();
        }
    };
}());

export { TogglePanel };
