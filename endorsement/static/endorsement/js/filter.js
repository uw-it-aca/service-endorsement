// 

var DisplayFilterPanel = {
    load: function () {
        this._registerEvents();
    },

    _registerEvents: function () {
        $('#app_content').on('change', 'select.display-filter', function(e) {
            var $panel = $(this).closest('.panel'),
                display = $panel.find('option:selected').val(),
                $rows = $panel.find('table tbody tr td .row');

            if (display === 'all') {
                $panel.find('table tbody tr').removeClass('visually-hidden');
                $rows.removeClass('visually-hidden');
            } else {
                $rows.addClass('visually-hidden');
                $panel.find('table tbody tr td .row.' + display + '_service').removeClass('visually-hidden');
                $panel.find('table tbody tr').each(function () {
                    var $tr = $(this);

                    $tr.addClass('visually-hidden');
                    $tr.find('.row').each(function () {
                        if ($(this).hasClass('visually-hidden') == false) {
                            $tr.removeClass('visually-hidden');
                            return false;
                        }
                    });
                });
            }
        })
    }
};
