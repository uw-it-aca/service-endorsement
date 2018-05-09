// javascript for service endorsement manager

$(window.document).ready(function() {
    registerEvents();
    $('[data-toggle="tooltip"]').tooltip();
});


var registerEvents = function() {
    $('button#search_endorsee').on('click', function (e) {
        $(this).button('loading');
        searchEndorsee();
    });

    $(document).on('endorse:UWNetIDsEndorseeResult', function (e, endorsements) {
        displayEndorsedUWNetIDs(endorsements);
    }).on('keypress', function (e) {
        if ($(e.target).attr('id', 'endorsee') && e.which == 13) {
            $('button#search_endorsee').button('loading');
            searchEndorsee();
            e.stopPropagation();
            e.preventDefault();
        }
    }).on('click', '[data-clipboard]', function () {
        var url = $(this).attr('data-clipboard'),
            $txt;

        $txt = $('textarea')
            .css('position', 'absolute')
            .css('left', '-2000px')
            .val(url)
            .appendTo(document.body);
        $txt.select();
        document.execCommand('copy');
        $txt.remove();
    });
};


var displayEndorsedUWNetIDs = function(endorsements) {
    var source = $("#admin-endorsee-search-result").html();
    var template = Handlebars.compile(source);

    $('#endorsees').html(template(endorsements));
    $('#endorsee-table').dataTable();
};


var displayEndorsedUWNetIDError = function(json_data) {
    var source = $("#admin-endorsee-search-error").html(),
        template = Handlebars.compile(source),
        context = {
            error: (json_data) ? (json_data.hasOwnProperty('error') ? json_data.error : json_data) : "Unknown error"
        };

    $('#endorsees').html(template(context));
};


var utc2local = function (utc_date) {
    var local = null,
        utc;

    if (utc_date) {
        utc = moment.utc(utc_date).toDate();
        local = moment(utc).local().format('YYYY-MM-DD HH:mm:ss');
    }

    return local;
};


var searchEndorsee = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;
    var netid = $('input#endorsee').val();

    $.ajax({
        url: "/api/v1/endorsee/" + netid,
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            // localize date
            $.each(results.endorsements, function () {
                this.datetime_endorsed = utc2local(this.datetime_endorsed);
                this.datetime_emailed = utc2local(this.datetime_emailed);
                this.datetime_renewed = utc2local(this.datetime_renewed);
                this.datetime_expired = utc2local(this.datetime_expired);
            });

            $(document).trigger('endorse:UWNetIDsEndorseeResult', [{
                endorsee: netid,
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
