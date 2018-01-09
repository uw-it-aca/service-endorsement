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
            $this.button('loading');
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
    }).on('change', '#endorse_o365, #endorse_google, #netid_list',  function(e) {
        enableCheckEligibility();
    }).on('input', '#netid_list', function () {
        enableCheckEligibility();
    }).on('click', 'input[name^="revoke_"]', function (e) {
//        $target = $(e.target);
//        if ($target.is(':checked')) {
//            $target.parent().prev().find('i').hide();
//        } else {
//            $target.parent().prev().find('i').show();
//        }

        enableRevocability();
    });

    $('a[href="#endorsed"]').on('shown.bs.tab', function () {
        getEndorsedUWNetIDs();
    });

    $(document).on('endorse:UWNetIDsValidated', function (e, validated) {
        $('button#validate').button('reset');
        displayValidatedUWNetIDs(validated);
    });

    $(document).on('endorse:UWNetIDsEndorseStatus', function (e, endorsed) {
        $('button#endorse').button('reset');
        displayEndorseResult(endorsed);
    });

    $(document).on('endorse:UWNetIDsRevokeStatus', function (e, endorsed) {
        $('button#revoke').button('reset');
        getEndorsedUWNetIDs();
    });

    $(document).on('endorse:UWNetIDsEndorsed', function (e, endorsed) {
        $('button#endorse').button('reset');
        displayEndorsedUWNetIDs(endorsed);
        enableRevocability();
    });
};

var enableCheckEligibility = function() {
    var netids = getNetidList();

    if (netids.length > 0 && (endorseOffice365() || endorseGoogle())) {
        $('#validate').removeAttr('disabled');
    } else {
        $('#validate').attr('disabled', 'disabled');
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

var endorseGoogle = function () {
    return $("#endorse_google").is(':checked');
};

var endorseOffice365 = function () {
    return $("#endorse_o365").is(':checked');
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
        endorse_o365: endorseOffice365(),
        endorse_google: endorseGoogle(),
        google_endorsable: false,
        o365_endorsable: false,
        netids: validated.validated
    };

    $.each(context.netids, function () {
        this.valid_netid = (this.error === undefined);

        if (this.google && this.google.error == undefined) {
            context.google_endorsable = true;
            this.google.eligible = true;
        }
        if (this.o365 && this.o365.error == undefined) {
            context.o365_endorsable = true;
            this.o365.eligible = true;
        }
    });

    $('#uwnetids-validated').html(template(context));

    $endorsement_group.attr('disabled', true);
    showValidationStep();
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
        endorse_o365: endorseOffice365(),
        endorse_google: endorseGoogle(),
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
            endorsed[this.netid] = {};

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
        endorse_o365: true,
        endorse_google: true,
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
