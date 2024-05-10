// javascript for service endorsement manager
/* jshint esversion: 6 */

import { MainTabs } from "./tabs.js";
import { ManageOfficeAccess } from "./tab/office.js";

$(window.document).ready(function() {
    registerEvents();
    $('[data-toggle="tooltip"]').tooltip();
    showInfoMessage('warning_1');
    MainTabs.load.apply(this);
});

var registerEvents = function() {
    $('button#generate_notification').on('click', function (e) {
        $(this).button('loading');
        generateNotification('service');
    });

    $('input.service').on('change', function (e) {
        generateNotification('service');
    });

    $('select#notification').on('change', function (e) {
        var $this = $(this);

        showInfoMessage($this.val());
        generateNotification($this.closest('div.tab').attr('id'));
    });

    $('select#access_type, select#delegate_type').on('change', function (e) {
        showInfoMessage($(this).val());
        generateNotification('access');
    });

    $('.tabs div#service').on('endorse:serviceTabExposed', function (e) {
        generateNotification('service');
    });

    $('.tabs div#shared_drive').on('endorse:shared_driveTabExposed', function (e) {
        showInfoMessage($('div.tab#shared_drive select#notification option:selected').val());
        generateNotification('shared_drive');
    });

    $('.tabs div#access').on('endorse:accessTabExposed', function (e) {
        if (window.access.hasOwnProperty('office') && window.access.office.hasOwnProperty('types')) {
            renderAccessTypes();
        } else {
            window.access.office = {};
            ManageOfficeAccess.getOfficeAccessTypes($('.tabs div#access'));
        }

        generateNotification('access');
    }).on('endorse:OfficeAccessTypesSuccess', function () {
        renderAccessTypes();
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

var renderAccessTypes = function () {
    var $select = $('select#access_type');

    if ($('option', $select).length < 2) {
        $.each(window.access.office.types, function () {
            $select.append($('<option>', {
                value: this.id,
                text : this.displayname
            }));
        });
    }
};

var generateNotification = function (notice_type) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
        data = {
            type: notice_type,
            notification: $("div.tab#" + notice_type + " select#notification option:selected").val()
        };

    if (notice_type == 'service') {
        data.endorsees = {};

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
    } else if (notice_type == 'access') {
        var delegate_type = $("select#delegate_type option:selected").val();
        var $access_type = $("select#access_type option:selected");

        if (data.notification === '' || $access_type.val() === '') {
            $('#notification_result').html("");
            return;
        }

        data.right = $access_type.val();
        data.right_name = $access_type.text();
        data.is_group = (delegate_type == 'group');
        data.is_shared_netid = (delegate_type == 'shared');
    } else if (notice_type == 'shared_drive') {
        var notification = $("select#notification option:selected").val();

        if (data.notification === '') {
            $('#notification_result').html("");
            return;
        }
    }

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
