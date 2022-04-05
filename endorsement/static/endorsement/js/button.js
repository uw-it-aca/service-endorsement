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
        }
    };
}());

export { Button };
