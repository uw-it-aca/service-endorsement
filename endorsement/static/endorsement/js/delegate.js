// javascript for service endorsement manager
/* jshint esversion: 6 */
import { DateTime } from "./datetime.js";
import { ClipboardCopy } from "./clipboard.js";

$(window.document).ready(function() {
    registerEvents();
    $('[data-toggle="tooltip"]').tooltip();
    ClipboardCopy.load.apply(ClipboardCopy);
    if ($('input#mailbox').val().length) {
        $('button#search_mailbox').click();
    }
});

var registerEvents = function() {
    $('button#search_mailbox').on('click', function (e) {
        $(this).button('loading');
        getMailboxDelegations($('input#mailbox').val());
    });

    $('button#sync_delegations').on('click', function (e) {
        $(this).button('loading');
        getMailboxDelegations($('input#mailbox').val(), true);
    });

    $(document).on('endorse:UWNetIDsDelegateResult', function (e, delegates) {
        displayDelegates(delegates);
    }).on('keypress', '[id="mailbox"]', function (e) {
        if (e.which == 13) {
            $('button#search_mailbox').button('loading');
            getMailboxDelegations($('input#mailbox').val());
            e.stopPropagation();
            e.preventDefault();
        }
    });
};


var displayDelegates = function(data) {
    var $table = $('#delegates .table tbody');
    $table.empty();

    $.each(data.delegates, function () {
        $table.append('<tr><td>' + data.mailbox +
                      '</td><td>' + this.delegate +
                      '</td><td>' + this.access_right +
                      '</td><td>' + (this.is_missing_record ? 'Missing Record' :
                                     this.is_stale_record ? 'Missing Delegation' :
                                     this.is_deleted_record ? 'Deleted Record' :
                                     this.is_right_mismatch ? 'Right Mismatch' : '') +
                      '</td></tr>');

        if (this.is_missing_record || this.is_stale_record || this.is_deleted_record || this.is_right_mismatch) {
            $('button#sync_delegations').prop('disabled', false);
        }
    });
};


var displayDelegatesError = function(json_data) {
    var //source = $("#admin-mailbox-search-error").html(),
//        template = Handlebars.compile(source),
        context = {
            error: (json_data) ? (json_data.hasOwnProperty('error') ? json_data.error : json_data) : "Unknown error"
        };

//    $('#delegates .delegate-notice').html(template(context));
    $('#delegates .delegate-notice').text(context.error);
    $('#delegates .table tbody').empty();
};


var getMailboxDelegations = function (netid, sync = false) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    // disable sync delegations button until results are returned
    $('button#sync_delegations').prop('disabled', true);
    $('#delegates .delegate-notice').text('');

    $.ajax({
        url: "/api/v1/mailbox/" + netid + (sync ? "?sync=true" : ""),
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:UWNetIDsDelegateResult', [{
                mailbox: netid,
                delegates: results.delegates
            }]);
        },
        error: function(xhr, status, error) {
            displayDelegatesError(xhr.responseJSON);
        },
        complete: function () {
            $('button#search_mailbox').button('reset');
            $('button#sync_delegations').button('reset');
        }
    });
};
