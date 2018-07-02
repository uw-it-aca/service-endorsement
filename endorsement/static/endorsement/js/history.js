// javascript to manage tab/hash changes

var HashHistory = {
    load: function () {
        this._registerEvents();
    },

    _registerEvents: function () {
        $(document).on('click', '.nav-tabs a[data-toggle="tab"]', function(e) {
            HashHistory._push($(this).attr('href'));
        }).on('click', '.tab-link', function(e) {
            var hash = $(this).attr('href');

            HashHistory._push(hash);
            $('a[href="'+ hash + '"]').tab('show');
        });

        $(window).bind('popstate', function (e) {
            if (e.originalEvent && e.originalEvent.state) {
                var hash = e.originalEvent.state.hash;

                $('a[href="'+ hash + '"]').tab('show');
            }
        });
    },

    _push: function (hash) {
        if (history.pushState) {
            history.pushState({ hash: hash }, null, hash);
        }
    },

    replace: function (hash) {
        history.replaceState({ hash: hash }, null, hash);
    }
};
