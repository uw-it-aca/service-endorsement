// javascript handling clipboard copying
/* jshint esversion: 6 */

var Button = (function () {
    var _showButtonLoading = function ($button) {
        var loading_text = $button.attr('data-loading-text'),
            spinner = '<i class="fa fa-circle-notch fa-spin"></i> ';

        if (loading_text) {
            $button.data('original_text', $button.html());
            $button.prop('disabled', true);
            $button.html(spinner + loading_text);
            
        }
    },
    _resetButtonLoading = function ($button) {
        var original_text = $button.data('original_text');

        if (original_text) {
            $button.html(original_text);
            $button.prop('disabled', false);
        }
    },
    _disableButton = function ($button) {
        $button.prop('disabled', true);
    },
    _enableButton = function ($button) {
        $button.prop('disabled', false);
    },
    _hideButton = function ($button) {
        $button.hide();
    },
    _showButton = function ($button) {
        $button.show();
    };

    return {
        loading: function ($button) {
            if ($button) {
                _showButtonLoading($button);
            }
        },
        reset: function ($button) {
            if ($button) {
                _resetButtonLoading($button);
            }
        },
        disable: function ($button) {
            if ($button) {
                _disableButton($button);
            }
        },
        enable: function ($button) {
            if ($button) {
                _enableButton($button);
            }
        },
        hide: function ($button) {
            if ($button) {
                _hideButton($button);
            }
        },
        show: function ($button) {
            if ($button) {
                _showButton($button);
            }
        }
    };
}());

export { Button };
