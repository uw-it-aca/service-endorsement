// javascript for service endorsement manager
/* jshint esversion: 6 */
import { DateTime } from "./datetime.js";
import { ClipboardCopy } from "./clipboard.js";

$(window.document).ready(function() {
    registerEvents();
    $('[data-toggle="tooltip"]').tooltip();
    initDataTable();
    ClipboardCopy.load.apply(ClipboardCopy);
    if ($('input#endorsee').val().length) {
        $('button#search_endorsee').click();
    }
});

var registerEvents = function() {
    $('button#search_endorsee').on('click', function (e) {
        $(this).button('loading');
        searchEndorsee($('input#endorsee').val());
    });

    $(document).on('endorse:UWNetIDsEndorseeResult', function (e, endorsements) {
        displayEndorsedUWNetIDs(endorsements);
    }).on('click', '.alpha-search', function (e) {
        var alpha = $(this).html();

        $('button#search_endorsee').button('loading');
        searchEndorsee(alpha.toLowerCase() + '.*');
        e.stopPropagation();
        e.preventDefault();
    }).on('keypress', '[id="endorsee"]', function (e) {
        if (e.which == 13) {
            $('button#search_endorsee').button('loading');
            searchEndorsee($('input#endorsee').val());
            e.stopPropagation();
            e.preventDefault();
        }
    });
};

var initDataTable = function () {
    $('#endorsee-table').dataTable({
        aaSorting: [[5, 'desc']],
        scrollY: '460px',
        scrollCollapse: true,
        paging: false,
        initComplete: function () {
                $('#show-revoked')
                    .prependTo('#endorsee-table_filter')
                    .css('display', 'inline-block')
                    .find('input')
                    .change(function () {
                        var api = $('#endorsee-table').dataTable().api();

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
        endorsee_source = $("#admin-endorsee-search-result-endorsee").html(),
        endorsee_shared_source = $("#admin-endorsee-search-result-endorsee-shared").html(),
        endorsee_template = Handlebars.compile(endorsee_source),
        endorsee_shared_template = Handlebars.compile(endorsee_shared_source),
        datetime_endorsed_source = $("#admin-endorsee-search-result-endorsee-datetime-endorsed").html(),
        datetime_endorsed_template = Handlebars.compile(datetime_endorsed_source),
        revoked_source = $("#admin-endorsee-search-result-endorsee-is-revoked").html(),
        revoked_template = Handlebars.compile(revoked_source),
        api = $('#endorsee-table').dataTable().api();

    api.clear().draw();

    if (endorsements.endorsements.endorsements.length) {
        $.each(endorsements.endorsements.endorsements, function () {
            api.row.add([
                endorsee_template(this).trim(),
                endorsee_shared_template(this).trim(),
                '<a href="/support/provisioner?netid=' + this.endorser.netid + '">' + this.endorser.netid + '</a>',
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
        window.history.pushState({}, '', window.location.pathname + '?netid=' + $('input#endorsee').val());
    } else {
        source = $("#admin-endorsee-empty-search-result").html();
        template = Handlebars.compile(source);
        $('#endorsee-table tbody').html(template(endorsements));
        $('div.dt-buttons button').attr('disabled', '1');
    }
};


var displayEndorsedUWNetIDError = function(json_data) {
    var source = $("#admin-endorsee-search-error").html(),
        template = Handlebars.compile(source),
        context = {
            error: (json_data) ? (json_data.hasOwnProperty('error') ? json_data.error : json_data) : "Unknown error"
        };

    $('#endorsees tbody').html(template(context));
};


var searchEndorsee = function (search_string) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/endorsee/" + search_string,
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

            $(document).trigger('endorse:UWNetIDsEndorseeResult', [{
                endorsee: search_string,
                endorsements: results
            }]);
        },
        error: function(xhr, status, error) {
            displayEndorsedUWNetIDError(xhr.responseJSON);
        },
        complete: function () {
            $('button#search_endorsee').button('reset');
        }
    });
};
