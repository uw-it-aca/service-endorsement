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

    $('input.service').on('change', function (e) {
        generateNotification();
    });

    $('select#notification').on('change', function (e) {
        showInfoMessage($(this).val());
        generateNotification();
    });

    $(document).on('endorse:NotificationResult', function (e, notification) {
        displayNotification(notification);
    });
};

var displayNotification = function(notification) {
    var template_source = $("#admin-notifications-result").html(),
        template = Handlebars.compile(template_source);

    $('#notification_result').html(template({
        subject: notification.subject,
        text: notification.text
    }));

    $('.notification-html').html(notification.html);
};

var showInfoMessage = function(opt) {
    $("div.info").hide();
    $("div.info#info_" + opt).show();

    var $extra_endorsees = $("div#endorsee2 .service, div#endorsee3 .service");
    if (opt == 'endorsee') {
        $extra_endorsees.attr("disabled", true);
    } else {
        $extra_endorsees.removeAttr("disabled");
    }
};

var displayNotificationError = function(json_data) {
    var template_source = $("#admin-notifications-error").html(),
        template = Handlebars.compile(template_source);

    $('#notification_result').html(template({
        text: json_data.hasOwnProperty('error') ? json_data.error : JSON.stringify(json_data)
    }));
};


var generateNotification = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
        data = {
            notification: $("select#notification option:selected").val(),
            endorsees: {}
        };

    if (!$(".service:enabled:checked").length) {
        $('#notification_result').html("");
        return;
    }

    $('div.endorsee').each(function () {
        var $this = $(this),
            netid = $this.attr('id');

        data.endorsees[netid] = [];
        $(".service:enabled:checked", $this).each(function () {
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
