// deal with table scrolling updates
/* jshint esversion: 6 */

import { History } from "./history.js";

var Scroll = (function () {
    var _track = function (container) {
        var $container = $(container);

        $('table tbody', $container).scroll(function (e) {
            _setNetidHash($container);
        });
    },

    _mouseover = function (container) {
        var $container = $(container);

        $container.mouseenter(function (e) {
            if (!$('#shared div.content > div').hasClass('loading') &&
                !$('#provisioned > div').hasClass('loading')) {
                _setNetidHash($container);
            }
        });
    },

    _setNetidHash = function ($container) {
        var netid = _firstVisibleNetid($container);

        if (netid) {
            History.replaceHash(netid);
        }
    },

    _firstVisibleNetid = function ($container) {
        var containerTop = $container.offset().top,
            $tbody = $('table tbody', $container),
            netid;

        $('tr', $tbody).each(function (index) {
            if ($(this).offset().top >= containerTop) {
                netid = _netidByIndex($tbody, index);
                return false;
            }
        });

        return netid;
    },

    _netidByIndex = function ($table, index) {
        return $table.find('tr').eq(index).attr('data-netid');
    },

    _scrollToNetid = function (netid) {
        var $tr = $('tr[data-netid="' + netid + '"]');

        if ($tr.length) {
            var top = $tr[0].offsetTop,
                $tbody = $tr.closest('tbody'),
                $thead = $tbody.prev('thead'),
                theadHeight = $thead.height();

            $tbody.scrollTop(top - theadHeight);
            History.replaceHash(netid);
        }
    };

    return {
        init: function (container) {
            _track(container);
            _mouseover(container);
            _scrollToNetid(window.location.hash.substr(1));
        }
    };
}());

export { Scroll };
