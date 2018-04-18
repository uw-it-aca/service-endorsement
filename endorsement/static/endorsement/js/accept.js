// javascript for service endorsement manager

$(window.document).ready(function() {
    displayPageHeader();
    displayPageBody();
    registerEvents();
});

var registerEvents = function() {
    $('#app_content').on('click', 'button#accept', function(e) {
        var $this = $(this);

        $this.button('loading');
        acceptEndorsement();
    });

    $(document).on('endorse:AcceptEndorsement', function (e, data) {
        var source = $("#endorse-accepted").html();
        var template = Handlebars.compile(source);
        $('#accept').html(template(window.endorsement));
    });
};

var displayPageBody = function() {
    var source = $("#endorse-accept").html();
    var template = Handlebars.compile(source);
    $('#accept').html(template(window.endorsement));
};

var displayPageHeader = function() {
    var source = $("#page-top").html();
    var template = Handlebars.compile(source);
    $("#top_banner").html(template({
        netid: window.user.netid
    }));
};

var acceptEndorsement = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/accept/",
        dataType: "JSON",
        data: JSON.stringify({ "accept_id": window.endorsement.accept_id }),
        type: "POST",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:AcceptEndorsement');
        },
        error: function(xhr, status, error) {
        }
    });
};
