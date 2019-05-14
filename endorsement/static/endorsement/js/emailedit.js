// common service endorse javascript

var EmailEdit = {
    load: function () {
        this._registerEvents();
    },

    _registerEvents: function () {
        $(document).on('click', '.start-email-edit', function (e) {
            var $email_editor = $(e.target).closest('.email-editor'),
                $display_email = $('.display-email', $email_editor),
                $edit_email = $('.edit-email', $email_editor),
                $edit = $('input', $edit_email);

            $display_email.addClass('visually-hidden');
            $edit_email.removeClass('visually-hidden');
            $edit.val($display_email.find('.shown-email').html());
            EmailEdit._checkValidEmail($edit);
            $edit.focus();
        }).on('click', '.finish-email-edit', function (e) {
            var $editor = $(e.target).closest('div.email-editor');

            EmailEdit._finishEmailEdit($('.edit-email input', $editor));
        }).on('change input', '.email-editor .edit-email input', function (e) {
            EmailEdit._checkValidEmail($(e.target));
        }).on('keypress', '.email-editor .edit-email input', function (e) {
            var $edit = $(e.target);

            if (e.which == 13) {
                EmailEdit._finishEmailEdit($edit);
            } else {
                EmailEdit._checkValidEmail($edit);
            }
        }).on('focusout', '.email-editor .edit-email input', function (e) {
            EmailEdit._finishEmailEdit($(e.target));
        });
    },

    getEditedEmail: function (netid) {
        var $input = $('.email-edit-' + netid + ' .edit-email input');

        return ($input.length) ? $input.val() : null;
    },

    _checkValidEmail: function ($edit) {
        var $edit_email = $edit.closest('.edit-email'),
            $icon = $('.finish-email-edit i', $edit_email);

        if (EmailEdit._validEmailAddress($edit.val())) {
            $edit_email.removeClass('error');
            $icon.removeClass("fa-minus-circle failure")
            $icon.addClass('fa-check success');
        } else {
            $icon.removeClass('fa-check success');
            $icon.addClass("fa-minus-circle failure")
            $edit_email.addClass('error');
        }
    },

    _finishEmailEdit: function($editor) {
        var email = $.trim($editor.val()),
            $email_editor = $editor.closest('.email-editor'),
            $display_email = $('.display-email', $email_editor),
            $edit_email = $('.edit-email', $email_editor);

        $('.shown-email', $email_editor).html(email);

        if (email.length && EmailEdit._validEmailAddress(email)) {
            $display_email.removeClass('visually-hidden');
            $edit_email.addClass('visually-hidden');
            
            // update success indicator
            $('.finish-edit-email i', $edit_email)
                .removeClass("fa-minus-circle failure")
                .addClass('fa-check success');
        } else {
            // show editor
            $display_email.addClass('visually-hidden');
            $edit_email.removeClass('visually-hidden');
            $('.editing-email', $edit_email).removeClass('visually-hidden');

            // update success indicator
            $('.finish-edit-email', $edit_email).find('>:first-child')
                .addClass("fa-minus-circle failure")
                .removeClass('fa-check success');
        }
    },

    _validEmailAddress: function(email_address, $editor) {
        var pattern = /^([a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+(\.[a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)*|"((([ \t]*\r\n)?[ \t]+)?([\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*(([ \t]*\r\n)?[ \t]+)?")@(([a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.)+([a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.?$/i,
            result = pattern.test(email_address);

        if ($editor) {
            $(document).trigger((result) ? 'endorse:UWNetIDsValidEmail' : 'endorse:UWNetIDsInvalidEmailError', [$editor]);
        }

        return result;
    }
};
