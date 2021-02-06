// javascript for service endorsement manager
/* jshint esversion: 6 */
$(window.document).ready(function() {
    registerEvents();
    $('[data-toggle="tooltip"]').tooltip();
});

var registerEvents = function() {
    $('button#generate_notification').on('click', function (e) {
        $(this).button('loading');
        generateNotification();
    });

    $(document).on('endorse:NotificationResult', function (e, notification) {
        displayNotification(notification);
    });
};

var displayNotification = function(notification) {
    $('#notification_text').html('<h4>Emailed Subject</h4><div>' + notification.subject + '</div><h4>Emailed HTML part</h4><div style="border: 1px solid #ccc; background-color: #f5f5f5;">' + notification.html + '</div><h4>Emailed Text Part</h4><pre>' + notification.text + '</pre>');
};


var displayNotificationError = function(json_data) {
    $('#notification_text').html(JSON.stringify(json_data));
};


var generateNotification = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;
    var data = {
        notification: $("select#notification option:selected").val(),
        endorsees: {}
    };

    $('div.endorsee').each(function () {
        var $this = $(this),
            netid = $this.attr('id');

        data.endorsees[netid] = [];
        $(".service:checked", $this).each(function () {
            data.endorsees[netid].push($(this).val());
        });
    });

    $.ajax({
        url: "/api/v1/notification/",
        type: "POST",
        data: JSON.stringify(data),
        contentType: "application/json",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:NotificationResult', [results]);
        },
        error: function(xhr, status, error) {
            displayNotificationError(xhr.responseJSON);
        },
        complete: function () {
            $('button#generate_notification').button('reset');
        }
    });
};
