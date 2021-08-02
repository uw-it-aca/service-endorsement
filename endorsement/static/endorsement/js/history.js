// manage history updates
/* jshint esversion: 6 */

var History = (function () {
    var _registerEvents= function () {
    },

    _replaceHash = function (hash) {
        if (hash) {
            history.replaceState({ hash: hash }, null, '#' + hash);
        }
    };

    return {
        replaceHash: _replaceHash
    };
}());

export { History };
