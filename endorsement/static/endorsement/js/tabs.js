// javascript for service endorsement manager
/* jshint esversion: 6 */
import { History } from "./history.js";

var MainTabs = (function () {
    var _registerEvents = function () {
        $(".tabs .tabs-list .tab-link").click(function(e){
            e.preventDefault();
            _openTab($(this).parent().attr("data-tab"));
        });

        $(window).on('popstate', function(event) {
            $(document).trigger('endorse:HistoryChange');
        });
    };

    // Exported functions
    var load = function () {
        _registerEvents();
    },
    _openTab = function (tab) {
        var $li = $(".tabs-list li[data-tab='" + tab + "']");

        if (! $li.hasClass('active')) {
            var $tab = $('.tabs div#' + tab);

            $(".tabs-list li, .tabs div.tab").removeClass("active");
            $li.addClass("active");
            $tab.addClass("active");
            $(document).attr('title', 'Provisioning Request Tool - ' + $('a', $li).text());
            $tab.trigger('endorse:' + tab + 'TabExposed');

            $(document).trigger('endorse:TabChange', [tab]);
        }
    };

    return {
        load: load,
        openTab: _openTab
    };
}());

export { MainTabs };
