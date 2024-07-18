// javascript for service endorsement manager
/* jshint esversion: 6 */
import { DateTime } from "./datetime.js";
import { ClipboardCopy } from "./clipboard.js";

$(window.document).ready(function() {
    registerEvents();
    $('[data-toggle="tooltip"]').tooltip();
    ClipboardCopy.load.apply(ClipboardCopy);
    if ($('input#member').val().length) {
        $('button#search_member').click();
    }
});

var registerEvents = function() {
    $('button#search_member').on('click', function (e) {
        $(this).button('loading');
        searchMember($('input#member').val());
    });

    $(document).on('endorse:UWNetIDsMemberResult', function (e, drives) {
        displaySharedDrives(drives);
    }).on('click', '.alpha-search', function (e) {
        var alpha = $(this).html();

        $('button#search_member').button('loading');
        searchMember(alpha.toLowerCase() + '.*');
        e.stopPropagation();
        e.preventDefault();
    }).on('keypress', '[id="member"]', function (e) {
        if (e.which == 13) {
            $('button#search_member').button('loading');
            searchMember($('input#member').val());
            e.stopPropagation();
            e.preventDefault();
        }
    });
};


var displaySharedDrives = function(drives) {
    var $accordion = $('#members .accordion'),
        card_source = $("#admin-member-search-result-card").html(),
        card_template = Handlebars.compile(card_source),
        result_source = $("#admin-member-search-result").html(),
        result_template = Handlebars.compile(result_source);

    $accordion.empty();
    if (drives.drives.drives.length) {
        $('#members .member-notice').html(result_template({member: $('input#member').val()}));

        $.each(drives.drives.drives, function (i) {
            $accordion.append(card_template({index: i, drive: this, content: this}));
        });

        window.history.pushState({}, '', window.location.pathname + '?netid=' + $('input#member').val());
    } else {
        result_source = $("#admin-member-empty-search-result").html();
        result_template = Handlebars.compile(result_source);

        $('#members .member-notice').html(result_template(drives));
    }
};


var displaySharedDrivesError = function(json_data) {
    var source = $("#admin-member-search-error").html(),
        template = Handlebars.compile(source),
        context = {
            error: (json_data) ? (json_data.hasOwnProperty('error') ? json_data.error : json_data) : "Unknown error"
        };

    $('#members .member-notice').html(template(context));
    $('#members .accordion').empty();
};


var searchMember = function (search_string) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/member/" + search_string,
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            // localize date
            $.each(results.drives, function () {
                this.datetime_accepted = DateTime.utc2local(this.datetime_accepted);
                this.datetime_expired = DateTime.utc2local(this.datetime_expired);
            });

            $(document).trigger('endorse:UWNetIDsMemberResult', [{
                member: search_string,
                drives: results
            }]);
        },
        error: function(xhr, status, error) {
            displaySharedDrivesError(xhr.responseJSON);
        },
        complete: function () {
            $('button#search_member').button('reset');
        }
    });
};
