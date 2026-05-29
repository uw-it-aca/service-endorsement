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
        searchMailbox($('input#mailbox').val());
    });

    $(document).on('endorse:UWNetIDsDelegateResult', function (e, delegates) {
        displayDelegates(delegates);
    }).on('keypress', '[id="mailbox"]', function (e) {
        if (e.which == 13) {
            $('button#search_mailbox').button('loading');
            searchMailbox($('input#mailbox').val());
            e.stopPropagation();
            e.preventDefault();
        }
    });
};


var displayDelegates = function(data) {
    var $table = $('#delegates .table tbody');
    $table.empty();

    $.each(data.delegates, function () {
        $table.append('<tr><td>' + data.mailbox + '</td><td>' + this.delegate + '</td><td>' + this.access_right + '</td><td></tr>');
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


var searchMailbox = function (search_string) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/mailbox/" + search_string,
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:UWNetIDsDelegateResult', [{
                mailbox: search_string,
                delegates: results.delegates
            }]);
        },
        error: function(xhr, status, error) {
            displayDelegatesError(xhr.responseJSON);
        },
        complete: function () {
            $('button#search_mailbox').button('reset');
        }
    });
};
