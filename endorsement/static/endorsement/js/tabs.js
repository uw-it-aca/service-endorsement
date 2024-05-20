// javascript for service endorsement manager
/* jshint esversion: 6 */
import { History } from "./history.js";

var MainTabs = (function () {
    var _registerEvents = function () {
        $(".tabs .tabs-list .tab-link").click(function(e){
            var $this = $(this),
                $li = $this.parent();

            e.preventDefault();

            if (! $li.hasClass('active')) {
                var tab = $li.attr("data-tab"),
                    $tab = $('.tabs div#' + tab);

                $(".tabs-list li, .tabs div.tab").removeClass("active");
                $li.addClass("active");
                $tab.addClass("active");
                $(document).attr('title', 'Provisioning Request Tool - ' + $('a', $li).text());
                $tab.trigger('endorse:' + tab + 'TabExposed');

                $(document).trigger('endorse:TabChange', [tab]);
            }
        });

        $(window).on('popstate', function(event) {
            $(document).trigger('endorse:HistoryChange');
        });
    };

    // Exported functions
    var load = function () {
        _registerEvents();
    };

    return {
        load: load,
    };
}());

export { MainTabs };
