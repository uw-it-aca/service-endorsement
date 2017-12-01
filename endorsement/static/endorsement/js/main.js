// javascript for service endorsement manager

$(window.document).ready(function() {
	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();
    enableCheckEligibility();
    registerEvents();
});


var registerEvents = function() {

    $('#app_content').on('click', 'input[type="button"]', function(e) {
        switch (e.target.id) {
        case 'validate':
            validationStep();
            break;
        case 'endorse':
            endorsementStep();
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
        $target = $(e.target);
        if ($target.is(':checked')) {
            $target.parent().prev().find('i').hide();
        } else {
            $target.parent().prev().find('i').show();
        }
    });

    $(document).on('endorse:UWNetIDsValidated', function (e, validated) {
        displayValidatedUWNetIDs(validated);
    });

    $(document).on('endorse:UWNetIDsEndorsed', function (e, endorsed) {
        displayEndorsedUWNetIDs(endorsed);
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


var validationStep = function() {
    validateUWNetids(getNetidList());
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
        google_revokable: false,
        o365_revokable: false,
        netids: validated
    };

    $.each(context.netids, function () {
        if (this.subscription.google.eligible) {
            context.google_endorsable = true;
        }
        if (this.subscription.o365.eligible) {
            context.o365_endorsable = true;
        }
        if (this.subscription.google.self_endorsed) {
            context.google_revokable = true;
        }
        if (this.subscription.o365.self_endorsed) {
            context.o365_revokable = true;
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
            window.endorsement = { validated: results };
            $(document).trigger('endorse:UWNetIDsValidated', [results]);
        },
        error: function(xhr, status, error) {
        }
    });
};


var endorsementStep = function() {
    endorseUWNetIDs(getValidNetidList());
};


var displayEndorsedUWNetIDs = function(endorsed) {
    var source = $("#endorsed-list").html();
    var template = Handlebars.compile(source);
    var context = {
        endorse_o365: endorseOffice365(),
        endorse_google: endorseGoogle(),
        endorsed: endorsed
    };

    // bind names back to netid
    $.each(endorsed, function () {
        var e = this;
        $.each(window.endorsement.validated, function () {
            if (e.netid === this.netid) {
                e.name = this.name;
                return false;
            }
        });
    });

    $('#uwnetids-endorsed').html(template(context));
    showEndorsedStep();
};


var endorseUWNetIDs = function(endorsees) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;
    var endorsed = {};

    $.each(window.endorsement.validated, function () {
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
            $(document).trigger('endorse:UWNetIDsEndorsed', [results]);
        },
        error: function(xhr, status, error) {
        }
    });
};


var getValidNetidList = function () {
    var to_endorse = {};
    var validated = [];

    $('input[name="endorse_o365"]:checked').each(function (e) {
        var netid = $(this).val();
        $.each(window.endorsement.validated, function () {
            if (netid == this.netid) {
                if (this.subscription.o365 &&
                    this.subscription.o365.eligible) {
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

    $('input[name="revoke_o365"]:checked').each(function (e) {
        var netid = $(this).val();
        $.each(window.endorsement.validated, function () {
            if (netid == this.netid) {
                if (this.subscription.o365 &&
                    this.subscription.o365.eligible) {
                    if (netid in to_endorse) {
                        to_endorse[this.netid].o365 = false;
                    } else {
                        to_endorse[this.netid] = {
                            o365: false
                        };
                    }
                }

                return false;
            }
        });
    });

    $('input[name="endorse_google"]:checked').each(function (e) {
        var netid = $(this).val();
        $.each(window.endorsement.validated, function () {
            if (netid == this.netid) {
                if (this.subscription.google &&
                    this.subscription.google.eligible) {
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

    $('input[name="revoke_google"]:checked').each(function (e) {
        var netid = $(this).val();
        $.each(window.endorsement.validated, function () {
            if (netid == this.netid) {
                if (this.subscription.google &&
                    this.subscription.google.eligible) {
                    if (netid in to_endorse) {
                        to_endorse[netid].google = false;
                    } else {
                        to_endorse[netid] = {
                            google: false
                        };
                    }
                }

                return false;
            }
        });
    });

    return to_endorse;
};


var showInputStep = function () {
    $('.endorsement-group input').removeAttr('disabled');
    $(['input.endorse_o365', 'input.endorse_google']);
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
