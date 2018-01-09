// javascript for service endorsement manager

$(window.document).ready(function() {
    registerEvents();
});


var registerEvents = function() {
    $('button#search_endorsee').on('click', function (e) {
        searchEndorsee();
    });

    $(document).on('endorse:UWNetIDsEndorseeResult', function (e, endorsements) {
        displayEndorsedUWNetIDs(endorsements);
    });

};


var displayEndorsedUWNetIDs = function(endorsements) {
    var source = $("#admin-endorsee-search-result").html();
    var template = Handlebars.compile(source);

    $('#endorsees').html(template(endorsements));
    $('#endorsee-table').dataTable();
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
            
            $(document).trigger('endorse:UWNetIDsEndorseeResult', [{
                endorsee: netid,
                endorsements: results
            }]);
        },
        error: function(xhr, status, error) {
        }
    });
};
