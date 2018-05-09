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

        $('#responsibility_modal').modal('toggle');
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

        $('#revoke_modal').modal('toggle');
        $('button[data-netid="' + netid + '"][data-service="' + service + '"]').button('loading');
        to_revoke[netid] = {};
        to_revoke[netid][service] = false;
        revokeUWNetIDs(to_revoke);
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
        var url = $(this).attr('data-clipboard'),
            msg = $(this).attr('data-clipboard-msg'),
            $txt;
        $txt = $('<input>')
            .css('position', 'absolute')
            .css('left', '-2000px')
            .val(url)
            .appendTo(document.body);
        $txt.select();
        document.execCommand('copy');
        $txt.remove();
        notify(msg);
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
        var $row = $(e.target).closest('tr'),
            $selected = $('option:selected', $row),
            value = $selected.val(),
            $options = $('option[value=' + value + ']');
        
        $options.prop('selected', true);
        if (value === 'other') {
            var $editor = $('.reason-editor', $row),
                reason = $.trim($editor.val());

            if (reason.length) {
                $('.reason-editor').val(reason);
                $('.editing-reason').removeClass('visually-hidden');
                $('.finish-edit-reason').removeClass('visually-hidden');
                $('.apply-all').removeClass('visually-hidden');
            }
        } else {
            $('.editing-reason').addClass('visually-hidden');
        }

        enableEndorsability();
    }).on('focusout', '.email-editor', function (e) {
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

                $('.reason-' + id).html('');
                $('.revoke-' + id).html('');
                $('.endorsed-' + id).html($("#unendorsed").html());
            });
        });
    }).on('endorse:UWNetIDsEndorsed', function (e, endorsed) {
        $('button#confirm_endorsements').button('reset');
        displayEndorsedUWNetIDs(endorsed);
    }).on('show.bs.modal', '#responsibility_modal' ,function (event) {
        var _modal = $(this);
        _modal.find('input#accept_responsibility').attr('checked', false);
        _modal.find('button#endorse').attr('disabled', 'disabled');
    });

    $('a[href="#endorsed"]').on('shown.bs.tab', function () {
        getEndorsedUWNetIDs();
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

var getReason = function ($row) {
    var $selected = $('.displaying-reasons select option:selected', $row);

    return ($selected.val() === 'other') ? $.trim($('.reason-editor', $row).val()) : $selected.html();
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

var revokeUWNetIDs = function(revokees) {
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
            $(document).trigger('endorse:UWNetIDsRevokeStatus', [
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

var notify = function (msg) {
    var $notify = $('.endorsement-notification');

    $notify.html(msg).css('display', 'block');
    $notify
        .css('top', $(document).scrollTop())
        .css('left', (($(document).width() - $notify.width())/2) + 'px')
        .fadeOut(3500);
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
