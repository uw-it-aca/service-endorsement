// javascript for service endorsement manager
/* jshint esversion: 6 */
import { DateTime } from "./datetime.js";
import { ClipboardCopy } from "./clipboard.js";

$(window.document).ready(function() {
    registerEvents();
    $('[data-toggle="tooltip"]').tooltip();
    initDataTable();
    ClipboardCopy.load.apply(ClipboardCopy);
    if ($('input#endorser').val().length) {
        $('button#search_endorser').click();
    }
});

var registerEvents = function() {
    $('button#search_endorser').on('click', function (e) {
        $(this).button('loading');
        searchEndorser($('input#endorser').val());
    });

    $(document).on('endorse:UWNetIDsEndorserResult', function (e, endorsements) {
        displayEndorsedUWNetIDs(endorsements);
    }).on('click', '.alpha-search', function (e) {
        var alpha = $(this).html();

        $('button#search_endorser').button('loading');
        searchEndorser(alpha.toLowerCase() + '.*');
        e.stopPropagation();
        e.preventDefault();
    }).on('keypress', '[id="endorser"]', function (e) {
        if (e.which == 13) {
            $('button#search_endorser').button('loading');
            searchEndorser($('input#endorser').val());
            e.stopPropagation();
            e.preventDefault();
        }
    });
};

var initDataTable = function () {
    $('#endorser-table').dataTable({
        aaSorting: [[5, 'desc']],
        scrollY: '460px',
        scrollCollapse: true,
        paging: false,
        initComplete: function () {
                $('#show-revoked')
                    .prependTo('#endorser-table_filter')
                    .css('display', 'inline-block')
                    .find('input')
                    .change(function () {
                        var api = $('#endorser-table').dataTable().api();

                        api.column(11).search(this.checked ? 'false' : '').draw();
                    });
            },
        dom: 'Bfrti',
        buttons: ['csv', 'print']
        });

    $('div.dt-buttons button').attr('disabled', '1');
};

var displayEndorsedUWNetIDs = function(endorsements) {
    var source,
        template,
        endorser_source = $("#admin-endorser-search-result-endorser").html(),
        endorser_shared_source = $("#admin-endorser-search-result-endorser-shared").html(),
        endorser_template = Handlebars.compile(endorser_source),
        endorser_shared_template = Handlebars.compile(endorser_shared_source),
        datetime_endorsed_source = $("#admin-endorser-search-result-endorser-datetime-endorsed").html(),
        datetime_endorsed_template = Handlebars.compile(datetime_endorsed_source),
        revoked_source = $("#admin-endorser-search-result-endorser-is-revoked").html(),
        revoked_template = Handlebars.compile(revoked_source),
        api = $('#endorser-table').dataTable().api();

    api.clear().draw();

    if (endorsements.endorsements.endorsements.length) {
        $.each(endorsements.endorsements.endorsements, function () {
            api.row.add([
                endorser_template(this).trim(),
                endorser_shared_template(this).trim(),
                '<a href="/support/provisionee?netid=' + this.endorsee.netid + '">' + this.endorsee.netid + '</a>',
                this.category_name,
                this.reason,
                this.datetime_emailed,
                this.datetime_notice_1_emailed,
                this.datetime_notice_2_emailed,
                this.datetime_notice_3_emailed,
                this.datetime_notice_4_emailed,
                datetime_endorsed_template(this),
                revoked_template(this).trim(),
                this.datetime_expired
            ]);
        });

        if ($('#show-revoked input:checked').length) {
            api.columns([11]).search('false').draw();
        } else {
            api.draw(true);
        }

        $('div.dt-buttons button').removeAttr('disabled');
    } else {
        source = $("#admin-endorser-empty-search-result").html();
        template = Handlebars.compile(source);
        $('#endorser-table tbody').html(template(endorsements));
        $('div.dt-buttons button').attr('disabled', '1');
    }
};


var displayEndorsedUWNetIDError = function(json_data) {
    var source = $("#admin-endorser-search-error").html(),
        template = Handlebars.compile(source),
        context = {
            error: (json_data) ? (json_data.hasOwnProperty('error') ? json_data.error : json_data) : "Unknown error"
        };

    $('#endorsers tbody').html(template(context));
};


var searchEndorser = function (search_string) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/endorser/" + search_string,
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            // localize date
            $.each(results.endorsements, function () {
                this.datetime_endorsed = DateTime.utc2local(this.datetime_endorsed);
                this.datetime_emailed = DateTime.utc2local(this.datetime_emailed);
                this.datetime_renewed = DateTime.utc2local(this.datetime_renewed);
                this.datetime_expired = DateTime.utc2local(this.datetime_expired);
            });

            $(document).trigger('endorse:UWNetIDsEndorserResult', [{
                endorser: search_string,
                endorsements: results
            }]);
        },
        error: function(xhr, status, error) {
            displayEndorsedUWNetIDError(xhr.responseJSON);
        },
        complete: function () {
            $('button#search_endorser').button('reset');
        }
    });
};
