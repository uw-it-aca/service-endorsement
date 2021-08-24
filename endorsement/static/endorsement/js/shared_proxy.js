// javascript for service endorsement manager
/* jshint esversion: 6 */

$(window.document).ready(function() {
    insertCSS();
    registerEvents();
});

var insertCSS = function () {
    $('head').append('<style> \
     .shared-netid-preamble { margin-top: 3rem; margin-bottom: 3rem; font-size: 1.6rem;} \
     .shared-netid-note-well { border: 1px solid black; background-color: cornsilk; padding: 1rem; } \
     .shared-netid-preamble span { font-weight: bold; } \
     .shared-netid-error { margin: 3rem; padding: 3rem; border: 1px solid blue; background-color: lightblue; } \
     .shared-netid-error p { padding-top: 2rem; padding-left: 1rem; font-size: 1.7rem; } \
     .proxy-shared-specific-reason { margin-left: 8rem; } \
     </style>')
};

var registerEvents = function() {
    $(document).on('endorse:EndorsementSharedOwnerResult', function (e, result) {
        window.shared_proxy = result;
        displaySharedProxy(result);
    }).on('endorse:EndorsementSharedOwnerError', function (e, error) {
        displaySharedProxyError(error);
    }).on('click', 'button#search_shared', function (e) {
        getEndorsementSharedOwner($('#shared_netid').val())
    }).on('change', '#proxy-shared-netid-service', function () {
        var service = $(this).val();

        $.each(window.shared_proxy.endorsements, function (svc, values) {
            if (service === svc) {
                setEndorsementSharedOwnerButton(service, values);
                return false;
            }
        });
    }).on('change', '#proxy-shared-netid-reason', function () {
        setEndorsementSharedOwnerReason($(this).val());
    }).on('click', '.proxy-provision-button button.endorse_service', function () {
        proxyProvisionSharedNetid(true);
    }).on('click', '.proxy-provision-button button.renew_service', function () {
        proxyProvisionSharedNetid(true);
    }).on('click', '.proxy-provision-button button.revoke_service', function () {
        proxyProvisionSharedNetid(false);
    }).on('endorse:EndorsementSharedProxySuccess', function (e, results) {
        displaySharedProxySuccess(results);
    }).on('endorse:EndorsementSharedProxyError', function (e, error) {
        displaySharedProxyError(error);
    });
};


var getEndorsementSharedOwner = function (shared_netid) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/shared_owner/" + shared_netid,
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:EndorsementSharedOwnerResult', [results]);
        },
        error: function(xhr, status, error) {
            $(document).trigger('endorse:EndorsementSharedOwnerError', [{
                shared_netid: shared_netid,
                message: xhr.responseJSON.error
            }])
        }
    });
};

var displaySharedProxy = function (shared_data) {
    var source = $("#shared-netid-provision-template").html(),
        template = Handlebars.compile(source);

    $('#provision_shared_netid').html(template(shared_data));
};

var displaySharedProxyError = function (error) {
    var source = $("#shared-netid-provision-error-template").html(),
        template = Handlebars.compile(source);

    $('#provision_shared_netid').html(template(error));
};

var setEndorsementSharedOwnerButton = function (service, values) {
    var source = $("#shared-netid-provision-button-template").html(),
        template = Handlebars.compile(source),
        context = values;

    context['svc'] = service;
    context['netid'] = window.shared_proxy.endorsee.netid;
    $('.proxy-provision-button').html(template(context));
    if ($('#proxy-shared-netid-reason option:selected').val().length) {
        proxyProvisionButtonEnabled(true);
    }
};

var setEndorsementSharedOwnerReason = function (reason) {
    proxyProvisionButtonEnabled(true);
    if (reason === 'other') {
        proxySpecificReasonEnabled(true);
    } else {
        proxySpecificReasonEnabled(false);
    }
};

var proxyProvisionButtonEnabled = function (state) {
    $('.proxy-provision-button button').prop("disabled", !state);
};

var proxySpecificReasonEnabled = function (state) {
    $('.proxy-shared-specific-reason').css("display", state ? 'block': 'none');
};

var proxyProvisionSharedNetid = function (endorse) {
    var service = $('#proxy-shared-netid-service option:selected').val(),
        reason_choice = $('#proxy-shared-netid-reason option:selected').val(),
        reason;;

    if (service.length <= 0) {
        alert('You need to pick a service!');
        return;
    }

    if (endorse) {
        if (reason_choice.length <= 0) {
            alert('You need to choose a reason!');
            return;
        } else if (reason_choice === 'other') {
            var specific = $.trim($('.proxy-shared-specific-reason input').val());

            if (specific.length) {
                reason = specific;
            } else {
                alert('You need to enter a specific reason!');
                return;
            }
        } else {
            reason = $('#proxy-shared-netid-reason option[value="' + reason_choice + '"]').val();
        }
    }

    provisionSharedNetidByProxy(service, reason, endorse);
}

var provisionSharedNetidByProxy = function (service, reason, endorse) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/shared_proxy/",
        type: "POST",
        data: JSON.stringify({
            "endorser": window.shared_proxy.endorser.netid,
            "endorsee": window.shared_proxy.endorsee.netid,
            "service": service,
            "reason": reason,
            "endorse": endorse ? 'true' : 'false'
        }),
        contentType: "application/json",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:EndorsementSharedProxySuccess', [results]);
        },
        error: function(xhr, status, error) {
            $(document).trigger('endorse:EndorsementSharedProxyError', [{
                message: xhr.responseJSON
            }])
        }
    });
};

var displaySharedProxySuccess = function (results) {
    var source = $("#shared-netid-provision-proxy-success-template").html(),
        template = Handlebars.compile(source);

    $('#shared_netid').val('');
    $('#provision_shared_netid').html(template(results));
};
