// javascript to manage tab/hash changes

var HashHistory = {
    load: function () {
        this._registerEvents();
    },

    _registerEvents: function () {
        $(document).on('click', '.nav-tabs a[data-toggle="tab"]', function(e) {
            if (history.pushState) {
                var hash = $(this).attr('href');

                history.pushState({ hash: hash }, null, hash);
            }

            e.preventDefault();
            e.stopPropagation();
        });

        $(window).bind('popstate', function (e) {
            var hash = e.originalEvent.state.hash;

            $('a[href="'+ hash + '"]').tab('show');
        });
    },

    replace: function (hash) {
        history.replaceState({ hash: hash }, null, hash);
    }
};
