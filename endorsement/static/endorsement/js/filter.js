// 

var DisplayFilterPanel = {
    load: function () {
        this._registerEvents();
    },

    _registerEvents: function () {
        $('#app_content').on('change', 'select.display-filter', function(e) {
            var $this = $(this),
                display = $('option:selected', $this).val(),
                $panel = $this.closest('.panel'),
                $rows = $('table tbody tr', $panel);

            if (display === 'all') {
                $rows.removeClass('visually-hidden');
            } else {
                $rows.addClass('visually-hidden');
                $('table tbody tr.' + display + '_service', $panel).removeClass('visually-hidden');
            }

            $panel.trigger('endorse:DisplayFilterChange');
        }).on('mousedown', 'select.display-filter', function(e) {
            var $this = $(this),
                $panel = $this.closest('.panel');

            $('option', $this).each(function () {
                $option = $(this);

                if ($option.val() != 'all') {
                    if ($('table tbody tr.' + $option.val() + '_service', $panel).length === 0) {
                        $option.attr('disabled', 'disabled');
                    } else {
                        $option.removeAttr('disabled');
                    }
                }
            });
        });
    }
};
