// manage history updates
/* jshint esversion: 6 */

var History = (function () {
    var _registerEvents= function () {
    },

    _replaceHash = function (hash) {
        if (hash) {
            history.replaceState({ hash: hash }, null, '#' + hash);
        }
    },

    _addPath = function (component) {
        var re = new RegExp('\/' + component + '$');

        if (! window.location.pathname.match(re)) {
            history.pushState({}, null, window.location.origin + '/' + component);
        }
    },

    _clipPath = function (component) {
        var re = new RegExp('\/' + component + '$');

        if (window.location.pathname.match(re)) {
            history.pushState({}, "", window.location.origin + '/' +
                              window.location.pathname.replace(re, ''));
        }
    },

    _clearPath = function () {
        var ids = [],
            re;

        $('.tabs .tab').each(function() {ids.push($(this).attr('id'));});
        re = new RegExp('\/(' + ids.join('|') + ')$');

        if (window.location.pathname.match(re)) {
            history.pushState({}, "", window.location.origin + '/' +
                              window.location.pathname.replace(re, ''));
        }
    };

    return {
        replaceHash: _replaceHash,
        addPath: _addPath,
        clipPath: _clipPath,
        clearPath: _clearPath
    };
}());

export { History };
