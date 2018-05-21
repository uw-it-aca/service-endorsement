// javascript for service endorsement manager

$(window.document).ready(function() {
	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();
    enableCheckEligibility();
    registerEvents();
});


var registerEvents = function() {
    $('#app_content').on('click', 'button#validate', function(e) {
        var $this = $(this);

        $this.button('loading');
        validateUWNetids(getNetidList());
    }).on('click', 'button#endorse', function(e) {
        var $this = $(this);

        $this.parents('.modal').modal('hide');
        $('#confirm_endorsements').button('loading').addClass('loading');
        endorseUWNetIDs(getEndorseNetids());
    }).on('click', '.confirm_revoke', function (event) {
        var $this = $(this),
            $modal = $('#revoke_modal');

        $('.modal-content', $modal).html(
            Handlebars.compile($("#revoke_modal_content").html())({
                netid: $this.attr('data-netid'),
                service: $this.attr('data-service'),
                service_name: $this.attr('data-service-name')
            }));

        $modal.modal({show:true});
    }).on('click', 'button#revoke', function(e) {
        var $this = $(this),
            netid = $this.attr('data-netid'),
            service = $this.attr('data-service'),
            to_revoke = {};

        $this.parents('.modal').modal('hide');
        $('button[data-netid="' + netid + '"][data-service="' + service + '"]').button('loading');
        to_revoke[netid] = {};
        to_revoke[netid][service] = false;
        revokeUWNetIDs(to_revoke, 
                       $this.attr('data-shared-netid') ? 'endorse:SharedUWNetIDsRevokeStatus' : 'endorse:UWNetIDsRevokeStatus');
    }).on('click', 'button.shared_endorse', function(e) {
        var $this = $(this),
            netid = $this.attr('data-netid'),
            service = $this.attr('data-service');

        sharedEndorseAcceptModal(netid, service);
    }).on('click', 'button.shared_revoke', function(e) {
        var $this = $(this),
            netid = $this.attr('data-netid'),
            service = $this.attr('data-service'),
            service_name = $this.attr('data-service-name');

        sharedEndorseRevokeModal(netid, service, service_name);
    }).on('click', 'button#netid_input', function(e) {
        var $this = $(this);

        showInputStep();
    }).on('click', 'button#new_netid_input', function(e) {
        var $this = $(this);

        $('#netid_list').val('');
        $('.endorsement-group input:checked').prop('checked', false);
        enableCheckEligibility();
        showInputStep();
    }).on('click', '[data-clipboard]', function (e) {
        copy_clipboard($(this));
    }).on('change', '#netid_list',  function(e) {
        enableCheckEligibility();
    }).on('change', '.displaying-reasons > select',  function(e) {
        var $row = $(e.target).closest('tr'),
            $selected = $('option:selected', $(this));

        if ($selected.val() === 'other') {
            var $editor = $('.reason-editor', $row),
                reason = $.trim($editor.val());

            $('.editing-reason', $row).removeClass('visually-hidden');
            if (reason.length) {
                $('.finish-edit-reason', $row).removeClass('visually-hidden');
                $('.apply-all', $row).removeClass('visually-hidden');
            } else {
                $('.finish-edit-reason', $row).addClass('visually-hidden');
                $('.apply-all', $row).addClass('visually-hidden');
            }

            $($editor, $row).focus();
        } else {
            $('.editing-reason', $row).addClass('visually-hidden');
            $('.apply-all', $row).removeClass('visually-hidden');
        }

        enableEndorsability();
    }).on('input', '#netid_list', function () {
        enableCheckEligibility();
    }).on('click', 'input[name^="endorse_"]', function (e) {
        enableEndorsability();
    }).on('click', '.edit-email', function (e) {
        var $row = $(e.target).closest('tr'),
            $editor = $('.email-editor', $row);

        if ($row.hasClass('unchecked')) {
            return false;
        }

        $('.displaying-email', $row).addClass('visually-hidden');
        $('.editing-email', $row).removeClass('visually-hidden');
        $editor.val($('.shown-email', $row).html());
        $editor.focus();
    }).on('click', '.finish-edit-email', function (e) {
        var $row = $(e.target).closest('tr');

        finishEmailEdit($('.email-editor', $row));
    }).on('click', '.apply-all', function (e) {
        var $td = $(e.target).closest('td'),
            $row = $(e.target).closest('tr'),
            $table = $(e.target).closest('table'),
            $selected = $('option:selected', $td),
            value = $selected.val(),
            $options = $('option[value=' + value + ']', $table);
        
        $options.prop('selected', true);
        if (value === 'other') {
            var $editor = $('.reason-editor', $row),
                reason = $.trim($editor.val());

            if (reason.length) {
                $('.reason-editor', $table).val(reason);
                $('.editing-reason', $table).removeClass('visually-hidden');
                $('.finish-edit-reason', $table).removeClass('visually-hidden');
                $('.apply-all', $table).removeClass('visually-hidden');
            }
        } else {
            $('.editing-reason').addClass('visually-hidden');
        }

        enableEndorsability();
    }).on('focusout', '.email-editor', function(e) {
        finishEmailEdit($(e.target));
    }).on('change', '#accept_responsibility',  function(e) {
        if (this.checked) {
            $('button#endorse').removeAttr('disabled');
        } else {
            $('button#endorse').attr('disabled', 'disabled');
        }
    });

    // broad delegation
    $(document).on('keypress', function (e) {
        if ($(e.target).hasClass('email-editor') && e.which == 13) {
            finishEmailEdit($(e.target));
        }
    }).on('input', function (e) {
        if ($(e.target).hasClass('reason-editor')) {
            if (e.which !== 13) {
                var $row = $(e.target).closest('tr'),
                    reason = $.trim($(e.target).val());

                if (reason.length) {
                    $('.finish-edit-reason', $row).removeClass('visually-hidden');
                    $('.apply-all', $row).removeClass('visually-hidden');
                } else {
                    $('.finish-edit-reason', $row).addClass('visually-hidden');
                    $('.apply-all', $row).addClass('visually-hidden');
                }
            }

            enableEndorsability();
        }
    }).on('endorse:UWNetIDsValidated', function (e, validated) {
        $('button#validate').button('reset');
        displayValidatedUWNetIDs(validated);
    }).on('endorse:UWNetIDsEndorseStatus', function (e, endorsed) {
        $('button#confirm_endorsements').button('reset');
        displayEndorseResult(endorsed);
    }).on('endorse:UWNetIDsRevokeStatus', function (e, data) {
        $.each(data.revokees, function (netid, endorsements) {
            $.each(endorsements, function (endorsement, state) {
                var id = endorsement + '-' + netid;

                $('#reason-' + id).html('');
                $('.revoke-' + id).html('');
                $('.endorsed-' + id).html($("#unendorsed").html());
            });

        });

    }).on('endorse:SharedUWNetIDsRevokeStatus', function (e, data) {
        updateSharedEndorsementStatus(data.revoked);
        enableEndorsability();
    }).on('endorse:UWNetIDsEndorsed', function (e, endorsed) {
        $('button#confirm_endorsements').button('reset');
        displayEndorsedUWNetIDs(endorsed);
    }).on('endorse:SharedUWNetIDsEndorseStatus', function (e, endorsed) {
        updateSharedEndorsementStatus(endorsed);
    }).on('endorse:SharedUWNetIDsEndorseSuccess', function (e, netid, service, service_name) {
        sharedEndorseSuccessModal(netid, service, service_name);
    }).on('endorse:SharedUWNetIDsEndorseStatusError', function (e, netid, service, error) {
        $('button[data-netid="' + netid + '"][data-service="' + service + '"].shared_endorse')
            .button('reset');
    }).on('endorse:UWNetIDsShared', function (e, shared) {
        displaySharedUWNetIDs(shared);
    }).on('click', 'button#confirm_shared_endorse', function(e) {
        var $this = $(this),
            netid = $this.attr('data-netid'),
            service = $this.attr('data-service'),
            reason = getReason($('#reason-' + service + '-' + netid)),
            to_revoke = {};

        $this.parents('.modal').modal('hide');
        $('button[data-netid="' + netid + '"][data-service="' + service + '"].shared_endorse')
            .button('loading');
        endorseSharedUWNetID(netid, service, reason);
    }).on('change', 'input[id^="shared_accept_responsibility"]', function(e) {
        if ($('input#shared_accept_responsibility_A')[0].checked
            && $('input#shared_accept_responsibility_B')[0].checked) {
            $('button#confirm_shared_endorse').removeAttr('disabled');
        } else {
            $('button#confirm_shared_endorse').attr('disabled', 'disabled');
        }
    }).on('change', '.displaying-reasons select',  function(e) {
        enableEndorsability();
    }).on('show.bs.modal', '#responsibility_modal' ,function (event) {
        var _modal = $(this);

        _modal.find('input#accept_responsibility').attr('checked', false);
        _modal.find('button#endorse').attr('disabled', 'disabled');
    }).on('show.bs.modal', '#shared_netid_modal' ,function (event) {
        var _modal = $(this);

        _modal.find('input#shared_accept_responsibility').attr('checked', false);
        _modal.find('button#confirm_shared_endorse').attr('disabled', 'disabled');
    });

    $('a[href="#endorsed"]').on('shown.bs.tab', function () {
        getEndorsedUWNetIDs();
    });

    $('a[href="#shared"]').on('shown.bs.tab', function () {
        // load once
        if ($('#shared table').length === 0) {
            getSharedUWNetIDs();
        }
    });

};

var finishEmailEdit = function($editor) {
    var email = $.trim($editor.val()),
        $row = $editor.closest('tr'),
        netid = $('.endorsed_netid', $row).html(),
        name = $('.endorsed_name', $row).html();

    // update shown email
    $('.shown-email', $row).html(email);

    if (email.length && validEmailAddress(email)) {
        // hide editor
        $('.editing-email', $row).addClass('visually-hidden');
        $('.displaying-email', $row).removeClass('visually-hidden');

        // update success indicator
        $('.finish-edit-email', $row).find('>:first-child')
            .removeClass("fa-minus-circle failure")
            .addClass('fa-check success');
    } else {
        // show editor
        $('.editing-email', $row).removeClass('visually-hidden');
        $('.displaying-email', $row).addClass('visually-hidden');

        // update success indicator
        $('.finish-edit-email', $row).find('>:first-child')
            .addClass("fa-minus-circle failure")
            .removeClass('fa-check success');
    }

    enableEndorsability();
};

var validEmailAddress = function(email_address) {
    var pattern = /^([a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+(\.[a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)*|"((([ \t]*\r\n)?[ \t]+)?([\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*(([ \t]*\r\n)?[ \t]+)?")@(([a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.)+([a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.?$/i;
    return pattern.test(email_address);
};

var getReason = function ($context) {
    var $selected = $('.displaying-reasons select option:selected', $context);

    return ($selected.val() === 'other') ? $.trim($('.reason-editor', $context).val()) : $selected.html();
};

var enableCheckEligibility = function() {
    var netids = getNetidList();

    if (netids.length > 0) {
        $('#validate').removeAttr('disabled');
    } else {
        $('#validate').attr('disabled', 'disabled');
    }
};

var enableEndorsability = function() {
    var $netids = $('.endorsed_netid'),
        endorsable = $netids.length > 0,
        unchecked = 0,
        $button = $('button#confirm_endorsements');

    $netids.each(function () {
        var $row = $(this).closest('tr');

        if ($('input[type="checkbox"]:checked', $row).length > 0) {
            $row.removeClass('unchecked');
            $(".email-editor", $row).removeAttr('disabled');
            if (!validEmailAddress($('.shown-email', $row).html()) ||
                    getReason($row).length <= 0) {
                endorsable = false;
            }
        } else {
            unchecked += 1;
            $row.addClass('unchecked');
            $(".email-editor", $row).attr('disabled', 'disabled');
        }
    });

    if (endorsable && unchecked < $netids.length) {
        $button.removeAttr('disabled');
    } else {
        $button.attr('disabled', 'disabled');
    }

    if (unchecked == $netids.length) {
        $button.addClass('no_netids');
    } else {
        $button.removeClass('no_netids');
    }

    if ($('.apply-all').length > 1) {
        $('.apply-all').removeClass('visually-hidden');
    } else {
        $('.apply-all').addClass('visually-hidden');
    }

    $('button.shared_endorse').each(function () {
        var $button = $(this),
            netid = $button.attr('data-netid'),
            service = $button.attr('data-service'),
            reason = getReason($('#reason-' + service + '-' + netid)),
            $apply_all = $('#reason-' + service + '-' + netid + ' .apply-all');

        if (reason && reason.length > 0) {
            $button.removeAttr('disabled');
            $apply_all.removeClass('link-disabled');
        } else {
            $button.attr('disabled', 'disabled');
            $apply_all.addClass('link-disabled');
        }
    });
};

var displayPageHeader = function() {
    var source = $("#page-top").html();
    var template = Handlebars.compile(source);
    $("#top_banner").html(template({
        netid: window.user.netid
    }));
};

var displayValidatedUWNetIDs = function(validated) {
    var source = $("#validated-list").html();
    var template = Handlebars.compile(source);
    var $endorsement_group = $('.endorsement-group input[type="checkbox"]');
    var context = {
        netids: validated.validated,
        netid_count: validated.validated.length
    };

    $.each(context.netids, function () {
        this.valid_netid = (this.error === undefined);

        if (this.google && this.google.error === undefined) {
            context.google_endorsable = true;
            this.google.eligible = true;
        }
        if (this.o365 && this.o365.error === undefined) {
            context.o365_endorsable = true;
            this.o365.eligible = true;
        }
    });

    $('#uwnetids-validated').html(template(context));

    $endorsement_group.attr('disabled', true);
    showValidationStep();
    enableEndorsability();

    $('.email-editor').each(function() {
        finishEmailEdit($(this));
    });
};

var validateUWNetids = function(netids) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/validate/",
        dataType: "JSON",
        data: JSON.stringify(netids),
        type: "POST",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            window.endorsement = { validation: results };
            $(document).trigger('endorse:UWNetIDsValidated', [results]);
        },
        error: function(xhr, status, error) {
        }
    });
};

var displayEndorseResult = function(endorsed) {
    var source = $("#endorse-result").html();
    var template = Handlebars.compile(source);
    var context = {
        can_revoke: false,
        has_endorsed: (endorsed && Object.keys(endorsed.endorsed).length > 0),
        endorsed: endorsed
    };

    $('#uwnetids-endorsed').html(template(context));
    showEndorsedStep();
};

var endorseUWNetIDs = function(endorsees) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;
    var endorsed = {};

    $.each(window.endorsement.validation.validated, function () {
        var endorsement = endorsees[this.netid];

        if (endorsement !== undefined) {
            endorsed[this.netid] = {
                'name': this.name,
                'email': endorsement.email,
                'reason': endorsement.reason
            };

            if (endorsement.o365 !== undefined) {
                endorsed[this.netid].o365 = endorsement.o365;
            }

            if (endorsement.google !== undefined) {
                endorsed[this.netid].google = endorsement.google;
            }
        }
    });

    $.ajax({
        url: "/api/v1/endorse/",
        dataType: "JSON",
        data: JSON.stringify(endorsed),
        type: "POST",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:UWNetIDsEndorseStatus', [results]);
        },
        error: function(xhr, status, error) {
        }
    });
};

var revokeUWNetIDs = function(revokees, event_id) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/endorse/",
        dataType: "JSON",
        data: JSON.stringify(revokees),
        type: "POST",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger(event_id, [
                {
                    revokees: revokees,
                    revoked: results
                }]);
        },
        error: function(xhr, status, error) {
        }
    });
};

var getEndorseNetids = function () {
    var to_endorse = {};
    var validated = [];

    $('input[name="endorse_o365"]:checked').each(function (e) {
        var netid = $(this).val(),
            $row = $(this).closest('tr'),
            email = $('.shown-email', $row).html(),
            reason = getReason($row);

        $.each(window.endorsement.validation.validated, function () {
            if (netid == this.netid) {
                if (this.o365 && this.o365.eligible) {
                    if (netid in to_endorse) {
                        to_endorse[this.netid].o365 = true;
                        to_endorse[this.netid].email = email;
                        to_endorse[this.netid].reason = reason;
                    } else {
                        to_endorse[this.netid] = {
                            o365: true,
                            email: email,
                            reason: reason
                        };
                    }
                }

                return false;
            }
        });
    });

    $('input[name="endorse_google"]:checked').each(function (e) {
        var netid = $(this).val(),
            $row = $(this).closest('tr'),
            email = $('.shown-email', $row).html(),
            reason = getReason($row);

        $.each(window.endorsement.validation.validated, function () {
            if (netid == this.netid) {
                if (this.google && this.google.eligible) {
                    if (netid in to_endorse) {
                        to_endorse[this.netid].google = true;
                        to_endorse[this.netid].email = email;
                        to_endorse[this.netid].reason = reason;
                    } else {
                        to_endorse[this.netid] = {
                            google: true,
                            email: email,
                            reason: reason
                        };
                    }
                }

                return false;
            }
        });
    });

    return to_endorse;
};

var displayEndorsedUWNetIDs = function(endorsed) {
    var source = $("#endorsed-netids").html();
    var template = Handlebars.compile(source);
    var context = {
        can_revoke: true,
        has_endorsed: (endorsed && Object.keys(endorsed.endorsed).length > 0),
        endorsed: endorsed
    };

    $('div.tab-pane#endorsed').html(template(context));
    $('div.tab-pane#endorsed ul').each(function () {
        var pending = $('.current-endorsee', this);

        if (pending.length) {
            pending.appendTo($(this));
        }
    });
};

var getEndorsedUWNetIDs = function() {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $('#endorsed').html($('#endorsed-loading').html());

    $.ajax({
        url: "/api/v1/endorsed/",
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:UWNetIDsEndorsed', [results]);
        },
        error: function(xhr, status, error) {
            $('#endorsed').html($('#endorsed-failure').html());
        }
    });
};

var displaySharedUWNetIDs = function(shared) {
    var source = $("#shared-netids").html();
    var template = Handlebars.compile(source);
    var context = {
        has_shared: false,
        shared: shared
    };

    $.each(shared.shared, function () {
        if (true) {
            context.has_shared = true;
            return false;
        }
    });

    $('div.tab-pane#shared').html(template(context));
    enableEndorsability();
};

var getSharedUWNetIDs = function() {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $('#shared').html($('#shared-loading').html());

    $.ajax({
        url: "/api/v1/shared/",
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:UWNetIDsShared', [results]);
        },
        error: function(xhr, status, error) {
            $('#shared').html($('#shared-failure').html());
        }
    });
};

var endorseSharedUWNetID = function(netid, service, reason) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
        endorsed = {};

    endorsed[netid] = {
        name: '',
        email: '',
        reason: reason,
        store: true
    };

    endorsed[netid][service] = true;

    $.ajax({
        url: "/api/v1/endorse/",
        dataType: "JSON",
        data: JSON.stringify(endorsed),
        type: "POST",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:SharedUWNetIDsEndorseStatus', [results]);
        },
        error: function(xhr, status, error) {
            $(document).trigger('endorse:SharedUWNetIDsEndorseStatusError', [netid, service, error]);
        }
    });
};

var sharedEndorseAcceptModal = function (netid, service) {
    var source = $("#shared_accept_modal_content").html(),
        template = Handlebars.compile(source),
        $modal = $('#shared_netid_modal');
        context = {
            netid: netid,
            service: service,
            is_o365: service == 'o365',
            is_google: service == 'google'
        };

    $('.modal-content', $modal).html(template(context));
    $modal.modal('show');
};

var sharedEndorseSuccessModal = function (netid, service, service_name) {
    var source = $("#shared_provisioned_modal_content").html(),
        template = Handlebars.compile(source),
        $modal = $('#shared_netid_modal');
        context = {
            netid: netid,
            service: service,
            service_name: service_name,
            is_o365: service == 'o365',
            is_google: service == 'google'
        };

    $('.modal-content', $modal).html(template(context));
    $modal.modal('show');
};

var updateSharedEndorsementStatus = function(endorsed) {
    var netid = Object.keys(endorsed.endorsed)[0],
        endorsement = endorsed.endorsed[netid],
        endorsers_template = Handlebars.compile(
            $("#endorsers_partial").html()),
        reason_template = Handlebars.compile(
            $("#reasons_partial").html()),
        action_template = Handlebars.compile(
            $("#endorse_button_partial").html());

    if (endorsement.hasOwnProperty('error')) {
        $('button[data-netid="' + netid + '"][data-service="o365"].shared_endorse')
            .button('reset');
        $('button[data-netid="' + netid + '"][data-service="google"].shared_endorse')
            .button('reset');
        return;
    }

    $.each(['o365', 'google'], function () {
        var service_id = this;

        if (endorsement.hasOwnProperty(service_id)) {
            $('#endorsers-' + service_id + '-' + netid).html(endorsers_template({
                endorser: endorsement[service_id].endorsed ? endorsement[service_id].endorser : null
            }));
            $('#reason-' + service_id + '-' + netid).html(reason_template({
                endorsement: endorsement[service_id].endorsed ? endorsement[service_id] : null
            }));
            $('#action-' + service_id + '-' + netid).html(action_template({
                netid: netid,
                endorsements: endorsement[service_id].endorsed ? endorsement[service_id] : null,
                service: service_id
            }));

            if (endorsement[service_id].endorsed) {
                $(document).trigger('endorse:SharedUWNetIDsEndorseSuccess',
                                    [netid, service_id, endorsement[service_id].category_name]);
            }
        }
    });
};

var sharedEndorseRevokeModal = function (netid, service, service_name) {
    var source = $("#shared_revoke_modal_content").html(),
        template = Handlebars.compile(source),
        $modal = $('#shared_netid_modal');
        context = {
            netid: netid,
            service: service,
            service_name: service_name,
            is_o365: service == 'o365',
            is_google: service == 'google'
        };

    $('.modal-content', $modal).html(template(context));
    $modal.modal('show');
};

var showInputStep = function () {
    $('.endorsement-group input').removeAttr('disabled');
    $('#uwnetids-validated').hide();
    $('#uwnetids-endorsed').hide();
    $('#uwnetids-input').show();
};

var showValidationStep = function () {
    $('.endorsement-group input').attr('disabled', true);
    $('#uwnetids-input').hide();
    $('#uwnetids-endorsed').hide();
    $('#uwnetids-validated').show();
};

var showEndorsedStep = function () {
    $('.endorsement-group input').attr('disabled', true);
    $('#uwnetids-input').hide();
    $('#uwnetids-validated').hide();
    $('#uwnetids-endorsed').show();
};

var getNetidList = function () {
    var netid_list = $('#netid_list').val().toLowerCase();
    if (netid_list) {
        return unique(netid_list
                      .replace(/\n/g, ' ')
                      .replace(/([a-z0-9]+)(@(uw|washington|u\.washington)\.edu)?/g, '$1')
                      .split(/[ ,]+/));
    }

    return [];
};

var unique = function(array) {
    return $.grep(array, function(el, i) {
        return el.length > 0 && i === $.inArray(el, array);
    });
};
