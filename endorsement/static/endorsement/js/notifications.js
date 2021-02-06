// javascript for service endorsement manager
/* jshint esversion: 6 */
$(window.document).ready(function() {
    registerEvents();
    $('[data-toggle="tooltip"]').tooltip();
    showInfoMessage('warning_1');
});

var registerEvents = function() {
    $('button#generate_notification').on('click', function (e) {
        $(this).button('loading');
        generateNotification();
    });

    $('select#notification').on('change', function (e) {
        showInfoMessage($(this).val());
    });

    $(document).on('endorse:NotificationResult', function (e, notification) {
        displayNotification(notification);
    });
};

var displayNotification = function(notification) {
    var box_style = 'style="border: 1px solid #ccc; background-color: #f5f5f5;"';

    $('#notification_text').html('<h4>Email Subject</h4><div ' + box_style + '>' + notification.subject + '</div><h4>Email HTML part</h4><div ' + box_style + '>' + notification.html + '</div><h4>Email Text Part</h4><pre>' + notification.text + '</pre>');
};

var showInfoMessage = function(opt) {
    $("div.info").hide();
    $("div.info#info_" + opt).show();

    var $extra_endorsees = $("div#endorsee_2 .service, div#endorsee_3 .service");
    if (opt == 'endorsee') {
        $extra_endorsees.attr("disabled", true);
    } else {
        $extra_endorsees.removeAttr("disabled");
    }
};

var displayNotificationError = function(json_data) {
    var text = "<h4>Error:</h4><div><pre>";

    if (json_data.hasOwnProperty('error')) {
        text += json_data.error;
    } else {
        text += JSON.stringify(json_data);
    }

    $('#notification_text').html(text + '</pre></div>');
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
