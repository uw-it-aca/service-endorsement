// javascript for service endorsement manager

$(window.document).ready(function() {
	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();
    enableCheckEligibility();
    registerEvents();
    if (window.location.hash === '#provision') {
        $('#netid_list:visible').focus();
    } else if (window.location.hash === '#provisioned') {
        $('a[href="#provisioned"]').tab('show');
    } else if (window.location.hash === '#shared') {
        $('a[href="#shared"]').tab('show');
    } else {
        history.replaceState({ hash: '#provision' }, null, '#provision');
        $('#netid_list:visible').focus();
    }
});


var registerEvents = function() {
    // in app events
    $('#app_content').on('click', 'button#validate', function(e) {
        var $this = $(this);

        $this.button('loading');
        validateUWNetids(getNetidList());
    }).on('click', 'button#endorse', function(e) {
        var $this = $(this);

        $this.parents('.modal').modal('hide');
        $('#confirm_endorsements').button('loading').addClass('loading');
        endorseUWNetIDs(getEndorseNetids());
    }).on('click', 'button#revoke', function(e) {
        var $this = $(this),
            netid = $this.attr('data-netid'),
            service = $this.attr('data-service'),
            to_revoke = {},
            $button = $('button[data-netid="' + netid + '"][data-service="' + service + '"]');

        $this.parents('.modal').modal('hide');
        $button.button('loading');
        to_revoke[netid] = {};
        to_revoke[netid][service] = false;
        revokeUWNetIDs(to_revoke, ($button.closest('div#shared-uwnetids').length) ? 'endorse:SharedUWNetIDsRevokeStatus' : 'endorse:UWNetIDsRevokeStatus');
    }).on('click', 'button#shared_update', function(e) {
        sharedEndorseAcceptModal(getSharedUWNetIDsToEndorse());
    }).on('click', 'button#netid_input', function(e) {
        showInputStep();
    }).on('click', 'button#new_netid_input', function(e) {
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
            if ($selected.val().length > 0) {
                $('.editing-reason', $row).addClass('visually-hidden');
                if ($('.displaying-reasons').length > 1) {
                    $('.apply-all.visually-hidden', $row).removeClass('visually-hidden');
                }
            }
        }

        enableSharedEndorsability();
        enableEndorsability();
    }).on('input', '#netid_list', function () {
        enableCheckEligibility();
    }).on('change', 'input[name^="endorse_"]', function (e) {
        enableEndorsability();
    }).on('change', 'input[id^="endorse_"]', function (e) {
        enableSharedEndorsability();
    }).on('change', 'input[id^="revoke_"]', function (e) {
        var $row = $(e.target).closest('tr'),
            $td = $(e.target).parent().parent().next(),
            $reason = $td.find('span'),
            $revoking = $td.find('span + span');

        if (this.checked) {
            $reason.addClass('visually-hidden');
            $revoking.removeClass('visually-hidden');
        } else {
            $reason.removeClass('visually-hidden');
            $revoking.addClass('visually-hidden');
        }

        enableSharedEndorsability();
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
            $('select.error', $table).removeClass('error');
            $('.editing-reason').addClass('visually-hidden');
            $('.apply-all', $table).removeClass('visually-hidden');
        }

        enableEndorsability();
        enableSharedEndorsability();
    }).on('click', '.tab-link', function (e) {
        var tab = $(e.target).attr('href');

        $('a[href="'+ tab + '"]').tab('show');
    }).on('focusout', '.email-editor', function(e) {
        finishEmailEdit($(e.target));
    }).on('change', '#accept_responsibility',  function(e) {
        if (this.checked) {
            $('button#endorse').removeAttr('disabled');
        } else {
            $('button#endorse').attr('disabled', 'disabled');
        }
    });

    // broad modal event delegation
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
            enableSharedEndorsability();
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
        enableSharedEndorsability();
    }).on('endorse:UWNetIDsEndorsed', function (e, endorsed) {
        $('button#confirm_endorsements').button('reset');
        displayEndorsedUWNetIDs(endorsed);
    }).on('endorse:SharedUWNetIDsEndorseStatus', function (e, endorsed) {
        updateSharedEndorsementStatus(endorsed);
        enableSharedEndorsability();
    }).on('endorse:SharedUWNetIDsEndorseSuccess', function (e, netid, service, service_name) {
        // pause for shared endorse modal fade
        $('button#shared_update').button('reset');
        setTimeout(function () {
            enableSharedEndorsability();
            sharedEndorseSuccessModal(netid, service, service_name);
        }, 500);
    }).on('endorse:SharedUWNetIDsEndorseStatusError', function (e, netid, service, error) {
        $('button#shared_update').button('reset');
    }).on('endorse:UWNetIDsInvalidReasonError', function (e, $row, $td) {
        if ($('input[type="checkbox"]:checked', $row).length > 0) {
            $td.addClass('error');
            $('button#shared_update').attr('disabled', 'disabled');
        }
    }).on('endorse:UWNetIDsInvalidEmailError', function (e, $row, $td) {
        if ($('input[type="checkbox"]:checked', $row).length > 0) {
            $td.addClass('error');
        }
    }).on('endorse:UWNetIDsShared', function (e, shared) {
        displaySharedUWNetIDs(shared);
    }).on('click', '.confirm_revoke', function (event) {
        var $this = $(this),
            $modal = $('#revoke_modal'),
            content_id = $this.closest('#shared-uwnetids').length ? '#shared_revoke_modal_content' : '#revoke_modal_content';

        $('.modal-content', $modal).html(
            Handlebars.compile($(content_id).html())({
                netid: $this.attr('data-netid'),
                service: $this.attr('data-service'),
                service_name: $this.attr('data-service-name')
            }));

        $modal.modal('show');
    }).on('click', 'button#confirm_shared_endorse', function(e) {
        $(this).parents('.modal').modal('hide');
        $('button#shared_update').button('loading');
        endorseSharedUWNetIDs(getSharedUWNetIDsToEndorse());
    }).on('click', '.nav-tabs a[data-toggle="tab"]', function(e) {
        if (history.pushState) {
            var hash = $(this).attr('href');

            history.pushState({ hash: hash }, null, hash);
        }

        e.preventDefault();
        e.stopPropagation();
    }).on('change', 'input[id^="shared_accept_responsibility"]', function(e) {
        var boxes = $('input[id^="shared_accept_responsibility"]').length,
            checked = $('input[id^="shared_accept_responsibility"]:checked').length;

        if (boxes === checked) {
            $('button#confirm_shared_endorse').removeAttr('disabled');
        } else {
            $('button#confirm_shared_endorse').attr('disabled', 'disabled');
        }
    }).on('shown.bs.tab', 'a[href="#provision"]', function (e) {
        $('#netid_list:visible').focus();
    }).on('shown.bs.tab', 'a[href="#provisioned"]', function (e) {
        getEndorsedUWNetIDs();
    }).on('shown.bs.tab', 'a[href="#shared"]', function (e) {
        // load once
        if ($('#shared table').length === 0) {
            getSharedUWNetIDs();
        }
    }).on('show.bs.modal', '#responsibility_modal' ,function (event) {
        var _modal = $(this);

        _modal.find('input#accept_responsibility').attr('checked', false);
        _modal.find('button#endorse').attr('disabled', 'disabled');
    }).on('show.bs.modal', '#shared_netid_modal' ,function (event) {
        var _modal = $(this);

        _modal.find('input#shared_accept_responsibility').attr('checked', false);
        _modal.find('button#confirm_shared_endorse').attr('disabled', 'disabled');
    });

    $(window).bind('popstate', function (e) {
        var hash = e.originalEvent.state.hash;

        $('a[href="'+ hash + '"]').tab('show');
    });
};

var finishEmailEdit = function($editor) {
    var email = $.trim($editor.val()),
        $td = $editor.closest('td'),
        $row = $td.closest('tr'),
        netid = $('.endorsed_netid', $row).html(),
        name = $('.endorsed_name', $row).html();

    // update shown email
    $('.shown-email', $row).html(email);

    if (email.length && validEmailAddress(email, $row, $td)) {
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

var validEmailAddress = function(email_address, $row, $td) {
    var pattern = /^([a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+(\.[a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)*|"((([ \t]*\r\n)?[ \t]+)?([\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*(([ \t]*\r\n)?[ \t]+)?")@(([a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.)+([a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.?$/i,
        result = pattern.test(email_address);
    if (!result) {
        $(document).trigger('endorse:UWNetIDsInvalidEmailError', [$row, $td]);
    }

    return result;
};

var getReason = function ($context) {
    var $selected = $('.displaying-reasons select option:selected', $context),
        reason = ($selected.length === 0 || $selected.val() === 'other') ? $.trim($('.reason-editor', $context).val()) : $selected.html();

    if (reason.length === 0 || $selected.val() === '') {
        $(document).trigger('endorse:UWNetIDsInvalidReasonError',
                            [$selected.closest('tr'), $selected.closest('td')]);
    }

    return reason;
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

    $('div#uwnetids-validated td.error').removeClass('error');
    $netids.each(function () {
        var $row = $(this).closest('tr'),
            $email = $('.shown-email', $row),
            $td = $email.closest('td'),
            reason = getReason($row);

        if ($('input[type="checkbox"]:checked', $row).length > 0) {
            $row.removeClass('unchecked');
            $(".email-editor", $row).removeAttr('disabled');
            if (!validEmailAddress($email.html(), $row, $td) ||
                    reason.length <= 0) {
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
};

var enableSharedEndorsability = function() {
    var $button = $('button#shared_update'),
        netids;

    $('td.error').removeClass('error');
    netids = getSharedUWNetIDsToEndorse();
    if (Object.keys(netids).length > 0 &&
            $('td.error').length === 0) {
        $button.removeAttr('disabled');
    } else {
        $button.attr('disabled', 'disabled');
    }
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

    $('div.tab-pane#provisioned').html(template(context));
    $('div.tab-pane#provisioned ul').each(function () {
        var pending = $('.current-endorsee', this);

        if (pending.length) {
            pending.appendTo($(this));
        }
    });
};

var getEndorsedUWNetIDs = function() {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $('#provisioned').html($('#endorsed-loading').html());

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
            $('#provisioned').html($('#endorsed-failure').html());
        }
    });
};

var displaySharedUWNetIDs = function(shared) {
    var source = $("#shared-netids").html(),
        template = Handlebars.compile(source),
        context = {
            has_shared: shared.shared && shared.shared.length > 0,
            shared: shared
        };

    $.each(context.shared.shared, function () {
        var endorsements = this.endorsements,
            svc;

        if (endorsements) {
            for (svc in endorsements) {
                if (endorsements.hasOwnProperty(svc)) {
                    if (endorsements[svc]) {
                        if (endorsements[svc].hasOwnProperty('datetime_endorsed')) {
                            endorsements[svc].date_endorsed = utc2localdate(endorsements[svc].datetime_endorsed);
                        }
                    }
                }
            }
        }
    });

    $('div.tab-pane#shared').html(template(context));
    enableSharedEndorsability();
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

var endorseSharedUWNetIDs = function(to_endorse) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/endorse/",
        dataType: "JSON",
        data: JSON.stringify(to_endorse),
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

var sharedEndorseAcceptModal = function (endorsements) {
    var source = $("#shared_accept_modal_content").html(),
        template = Handlebars.compile(source),
        $modal = $('#shared_netid_modal'),
        endorse_o365 = [],
        endorse_google = [],
        context = {
            endorse_o365: [],
            endorse_google: [],
            endorse_netid_count: 0,
            endorse_o365_netid_count: 0,
            endorse_google_netid_count: 0
        },
        netid;

    for (netid in endorsements) {
        if (endorsements.hasOwnProperty(netid)) {
            if (endorsements[netid].hasOwnProperty('o365')) {
                context.endorse_o365.push(netid);
            }

            if (endorsements[netid].hasOwnProperty('google')) {
                context.endorse_google.push(netid);
            }
        }
    }

    context.endorse_o365_netid_count = context.endorse_o365.length;
    context.endorse_google_netid_count = context.endorse_google.length;
    context.endorse_netid_count = context.endorse_google_netid_count + context.endorse_o365_netid_count;

    $.data($modal[0], 'modal-body-context', context);

    $('.modal-content', $modal).html(template(context));
    $modal.modal('show');
};

var sharedEndorseSuccessModal = function (netid, service, service_name) {
    var source = $("#shared_provisioned_modal_content").html(),
        template = Handlebars.compile(source),
        $modal = $('#shared_netid_modal'),
        context = $.data($modal[0], 'modal-body-context');

    $('.modal-content', $modal).html(template(context));
    $modal.modal('show');
};

var getSharedUWNetIDsToEndorse = function () {
    var endorsees = {};

    $.each(['o365', 'google'], function () {
        var service_id = this;

        $('input[id^="endorse_' + service_id + '_"]:checked').each(function () {
            var $row = $(this).closest('tr'),
                netid = this.value;

            if (!endorsees.hasOwnProperty(netid)) {
                endorsees[netid] = {
                    name: '',
                    email: '',
                    reason: getReason($row),
                    store: true
                };
            }

            endorsees[netid][service_id] = true;
        });
    });

    return endorsees;
};

var updateSharedEndorsementStatus = function(endorsed) {
    var endorsers_template = Handlebars.compile(
            $("#endorsers_partial").html()),
        reason_template = Handlebars.compile(
            $("#reasons_partial").html()),
        action_template = Handlebars.compile(
            $("#endorse_button_partial").html()),
        success = false,
        netid;

    $.each(endorsed.endorsed, function(netid, endorsements) {
        $.each(['o365', 'google'], function () {
            var service_id = this,
                endorsement,
                $row;

            if (endorsements.hasOwnProperty('error')) {
                $('button.shared_update').button('reset');
                return;
            }

            if (endorsements.hasOwnProperty(service_id)) {
                endorsement = endorsements[service_id];
                $row = $('#endorsers-' + service_id + '-' + netid).closest('tr');

                if (endorsement.hasOwnProperty('datetime_endorsed')) {
                    endorsement.date_endorsed = utc2localdate(endorsement.datetime_endorsed);
                }
                
                $('#endorsers-' + service_id + '-' + netid).html(endorsers_template({
                    netid: netid,
                    svc: service_id,
                    endorsement: endorsement.endorsed ? endorsement : null
                }));

                $('#reason-' + service_id + '-' + netid).html(reason_template({
                    endorsements: endorsement.endorsed ? endorsements : null
                }));

                if (endorsement.endorsed || $('button.confirm_revoke', $row).length === 0) {
                    $('#reason-' + netid).html(reason_template({
                        endorsements: endorsement.endorsed ? endorsements : null
                    }));
                }

                if (!success && endorsement.endorsed) {
                    success = true;
                }
            }
        });
    });

    if (success) {
        $(document).trigger('endorse:SharedUWNetIDsEndorseSuccess', [endorsed]);
    }
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
