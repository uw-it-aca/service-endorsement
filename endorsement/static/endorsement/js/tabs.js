// javascript for service endorsement manager
/* jshint esversion: 6 */

var MainTabs = (function () {
    var _registerEvents = function () {
        $(".tabs .tabs-list li span").click(function(e){
            e.preventDefault();
        });

        $(".tabs .tabs-list li span").click(function(){
            var $li = $(this).parent();

            if (! $li.hasClass('active')) {
                var tab = $li.attr("data-tab"),
                    $tab = $('.tabs div#' + tab);

                $(".tabs-list li, .tabs div.tab").removeClass("active");
                $li.addClass("active");
                $tab.addClass("active");
                $tab.trigger('endorse:MainTabExposed');
            }
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
