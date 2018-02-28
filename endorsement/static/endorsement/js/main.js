// javascript for service endorsement manager

$(window.document).ready(function() {
	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();
    enableCheckEligibility();
    registerEvents();
});


var registerEvents = function() {
    $('#app_content').on('click', 'button[type="button"]', function(e) {
        var $this = $(this);

        switch (e.target.id) {
        case 'validate':
            $this.button('loading');
            validateUWNetids(getNetidList());
            break;
        case 'endorse':
            $('#responsibility_modal').modal('toggle');
            $('#confirm_endorsements').button('loading');
            endorseUWNetIDs(getEndorseNetids());
            break;
        case 'revoke':
            $this.button('loading');
            revokeUWNetIDs(getRevokedNetids());
            break;
        case 'netid_input':
            showInputStep();
            break;
        case 'new_netid_input':
            $('#netid_list').val('');
            $('.endorsement-group input:checked').prop('checked', false);
            enableCheckEligibility();
            showInputStep();
            break;
        default: break;
        }
    }).on('change', '#netid_list',  function(e) {
        enableCheckEligibility();
    }).on('input', '#netid_list', function () {
        enableCheckEligibility();
    }).on('click', 'input[name^="endorse_"]', function (e) {
        enableEndorsability();
    }).on('click', 'input[name^="revoke_"]', function (e) {
        enableRevocability();
    }).on('click', '.edit-email', function (e) {
        var $row = $(e.target).closest('tr'),
            $editor = $('.email-editor', $row);

        $('.displaying-email', $row).addClass('visually-hidden');
        $('.editing-email', $row).removeClass('visually-hidden');
        $editor.val($('.shown-email', $row).html());
        $editor.focus();
    }).on('click', '.finish-edit-email', function (e) {
        var $row = $(e.target).closest('tr');

        finishEmailEdit($('.email-editor', $row));
    }).on('focusout', '.email-editor', function (e) {
        finishEmailEdit($(e.target));
    }).on('change', '#accept_responsibility',  function(e) {
        if (this.checked) {
            $('button#endorse').removeAttr('disabled');
        } else {
            $('button#endorse').attr('disabled', 'disabled');
        }
    });

    $(document).on('keypress', function (e) {
        if ($(e.target).hasClass('email-editor') && e.which == 13) {
            finishEmailEdit($(e.target));
        }
    });

    $('a[href="#endorsed"]').on('shown.bs.tab', function () {
        getEndorsedUWNetIDs();
    });

    $(document).on('endorse:UWNetIDsValidated', function (e, validated) {
        $('button#validate').button('reset');
        displayValidatedUWNetIDs(validated);
    });

    $(document).on('endorse:UWNetIDsEndorseStatus', function (e, endorsed) {
        $('button#confirm_endorsements').button('reset');
        displayEndorseResult(endorsed);
    });

    $(document).on('endorse:UWNetIDsRevokeStatus', function (e, endorsed) {
        $('button#revoke').button('reset');
        getEndorsedUWNetIDs();
    });

    $(document).on('endorse:UWNetIDsEndorsed', function (e, endorsed) {
        $('button#confirm_endorsements').button('reset');
        displayEndorsedUWNetIDs(endorsed);
        enableRevocability();
    });

    $(document).on('show.bs.modal', function (event) {
        var _modal = $(this);
        _modal.find('input#accept_responsibility').attr('checked', false);
        _modal.find('button#endorse').attr('disabled', 'disabled');
    });
};

var finishEmailEdit = function($editor) {
    var email = $.trim($editor.val()),
        $row = $editor.closest('tr'),
        netid = $('.endorsed_netid', $row).html(),
        name = $('.endorsed_name', $row).html();

    // update shown email
    $('.shown-email', $row).html(email);

    // update email in validated list
    $.each(window.endorsement.validation.validated, function () {
        if (netid == this.netid) {
            this.email = email;
            return false;
        }
    });

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

var validEmailAddresses = function() {
    var valid = true;

    $('.shown-email').each(function() {
        var $row = $(this).closest('tr');

        if (!validEmailAddress($(this).html()) && 
            $('input[type="checkbox"]:checked', $row).length > 0) {
            $row.addClass('no-endorsement');
            valid = false;
        } else {
            $row.removeClass('no-endorsement');
        }
    });

    return valid;
};

var validEmailAddress = function(email_address) {
    var pattern = /^([a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+(\.[a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)*|"((([ \t]*\r\n)?[ \t]+)?([\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*(([ \t]*\r\n)?[ \t]+)?")@(([a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.)+([a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.?$/i;
    return pattern.test(email_address);
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
    var netids = getEndorseNetids();

    if (Object.keys(netids).length && validEmailAddresses()) {
        $('button#confirm_endorsements').removeAttr('disabled');
    } else {
        $('button#confirm_endorsements').attr('disabled', 'disabled');
    }
};

var enableRevocability = function() {
    var netids = getRevokedNetids();

    if (Object.keys(netids).length) {
        $('#revoke').removeAttr('disabled');
    } else {
        $('#revoke').attr('disabled', 'disabled');
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
                'email': this.email
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
            $(document).trigger('endorse:UWNetIDsRevokeStatus', [results]);
        },
        error: function(xhr, status, error) {
        }
    });
};

var getEndorseNetids = function () {
    var to_endorse = {};
    var validated = [];

    $('input[name="endorse_o365"]:checked').each(function (e) {
        var netid = $(this).val();
        $.each(window.endorsement.validation.validated, function () {
            if (netid == this.netid) {
                if (this.o365 && this.o365.eligible) {
                    if (netid in to_endorse) {
                        to_endorse[this.netid].o365 = true;
                    } else {
                        to_endorse[this.netid] = {
                            o365: true
                        };
                    }
                }

                return false;
            }
        });
    });

    $('input[name="endorse_google"]:checked').each(function (e) {
        var netid = $(this).val();
        $.each(window.endorsement.validation.validated, function () {
            if (netid == this.netid) {
                if (this.google && this.google.eligible) {
                    if (netid in to_endorse) {
                        to_endorse[this.netid].google = true;
                    } else {
                        to_endorse[this.netid] = {
                            google: true
                        };
                    }
                }

                return false;
            }
        });
    });

    return to_endorse;
};

var getRevokedNetids = function () {
    var to_revoke = {};
    var validated = [];

    $('input[name="revoke_o365"]:checked').each(function () {
        addRevocation($(this).val(), 'o365', to_revoke);
    });

    $('input[name="revoke_google"]:checked').each(function () {
        addRevocation($(this).val(), 'google', to_revoke);
    });

    return to_revoke;
};

var addRevocation = function (netid, service, to_revoke) {
    if (!(netid in to_revoke)) {
        to_revoke[netid] = {};
    }

    to_revoke[netid][service] = false;
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
};

var getEndorsedUWNetIDs = function() {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

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

var getNetidList = function () {
    return unique($('#netid_list').val().replace(/\n/g, ' ').split(/[ ,]+/));
};

var unique = function(array) {
    return $.grep(array, function(el, i) {
        return el.length > 0 && i === $.inArray(el, array);
    });
};
