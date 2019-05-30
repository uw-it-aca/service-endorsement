// 

var Reasons = {
    load: function () {
        this._registerEvents();
    },

    _registerEvents: function () {
        $('#app_content').on('change', '.displaying-reasons > select',  function(e) {
            var $target = $(e.target),
                $row = $target.closest('tr'),
                $selected = $('option:selected', $(this)),
                $panel = $row.parents('.panel');

            if ($selected.val() === 'other') {
                var $editor = $('.reason-editor', $row),
                    reason = $.trim($editor.val());

                $('.editing-reason', $row).removeClass('visually-hidden');
                if (reason.length) {
                    $('.finish-edit-reason', $row).removeClass('visually-hidden');
                    $('.apply-reason', $row).removeClass('visually-hidden');
                } else {
                    $('.finish-edit-reason', $row).addClass('visually-hidden');
                    $('.apply-reason', $row).addClass('visually-hidden');
                }

                $($editor, $row).focus();
            } else {
                if ($selected.val().length > 0) {
                    $('.editing-reason', $row).addClass('visually-hidden');
                    if ($('.displaying-reasons').length > 1) {
                        $('.apply-reason.visually-hidden', $row).removeClass('visually-hidden');
                    }
                }
            }

            $panel.trigger('endorse:UWNetIDChangedReason', [$row]);
        }).on('click', '.apply-all, .apply-unset', function (e) {
            var $target = $(e.target),
                $reason = $target.closest('div.endorse-reason'),
                $table = $target.closest('table'),
                $panel = $table.parents('.panel'),
                $selected = $('option:selected', $reason),
                value = $selected.val();

            if ($target.hasClass('apply-unset')) {
                $('option[value=""]:selected', $table)
                    .closest('select')
                    .find('option[value=' + value + ']')
                    .prop('selected', true);
            } else {
                $('option[value=' + value + ']', $table).prop('selected', true);
            }

            if (value === 'other') {
                var $editor = $('.reason-editor', $reason),
                    reason = $.trim($editor.val());

                if (reason.length) {
                    $('.reason-editor', $table).val(reason);
                    $('.editing-reason', $table).removeClass('visually-hidden');
                    $('.finish-edit-reason', $table).removeClass('visually-hidden');
                    $('.apply-reason', $table).removeClass('visually-hidden');
                }
            } else {
                $('select.error', $table).removeClass('error');
                $('.editing-reason').addClass('visually-hidden');
                $('.apply-reason', $table).removeClass('visually-hidden');
            }

            $panel.trigger('endorse:UWNetIDApplyAllReasons');
        }).on('input', function (e) {
            var $target = $(e.target),
                $panel = $target.parents('.panel');

            if ($target.hasClass('reason-editor')) {
                if (e.which !== 13) {
                    var $row = $(e.target).closest('tr'),
                        reason = $.trim($(e.target).val());

                    if (reason.length) {
                        $('.finish-edit-reason', $row).removeClass('visually-hidden');
                        $('.apply-reason', $row).removeClass('visually-hidden');
                    } else {
                        $('.finish-edit-reason', $row).addClass('visually-hidden');
                        $('.apply-reason', $row).addClass('visually-hidden');
                    }
                }

                $panel.trigger('endorse:UWNetIDReasonEdited');
            }
        });
    },

    getReason: function ($context) {
        var $select = $('.displaying-reasons select', $context),
            $selected = $('option:selected', $select),

            reason = ($select.prop('selectedIndex') === 0) ? "" : ($selected.length === 0 || $selected.val() === 'other') ? $.trim($('.reason-editor', $context).val()) : $selected.html(),
            $panel = $context.parents('.panel');

        if (reason.length === 0 || $selected.val() === '') {
            $panel.trigger('endorse:UWNetIDsInvalidReasonError',
                           [$selected.closest('tr'), $selected.closest('td')]);
        }

        return reason;
    }
};
