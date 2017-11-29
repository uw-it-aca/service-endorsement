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
        netids: validateUWNetids(getNetidList())
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
    var validated = [];

    $.each(netids, function (i, netid) {


        /// FAKE WEB SERVICE RESPONSES
        var valid_netid = Math.random() > 0.15;
        var eligible_netid = valid_netid ? Math.random() > 0.1 : false;

        var o365_active = eligible_netid ? Math.random() < 0.3 : false;
        var o365_endorsers = null;
        var o365_by_you = false;
        if (o365_active && Math.random() > 0.3) {
            o365_by_you = o365_active ? Math.random() < 0.5 : false;
            o365_endorsers = [o365_by_you ? 'you' : 'mumble'];
            if (Math.random() < .5) {
                    o365_endorsers.push('garble');
            }
            if (Math.random() < .5) {
                    o365_endorsers.push('marble');
            }
        }


        var google_active = eligible_netid ? Math.random() < 0.3 : false;
        var google_endorsers = null;
        var google_by_you = false;
        if (google_active && Math.random() > 0.3) {
            google_by_you = google_active ? Math.random() < 0.5 : false;
            google_endorsers = [google_by_you ? 'you' : 'mumble'];
            if (Math.random() < .5) {
                    google_endorsers.push('garble');
            }
            if (Math.random() < .5) {
                    google_endorsers.push('marble');
            }
        }
        //// end of web service fakery




        validated.push({
            netid: netid,
            valid_netid: valid_netid,
            name: netid + '. Lastname',
            email: netid + '@uw.edu',
            subscription: {
                google: {
                    eligible: eligible_netid,
                    active: google_active,
                    endorsers: google_endorsers,
                    self_endorsed: google_by_you,
                    error: null
                },
                o365: {
                    eligible: eligible_netid,
                    active: o365_active,
                    endorsers: o365_endorsers,
                    self_endorsed: o365_by_you,
                    error: null
                }
            }
        });
    });

    window.endorsement = {};
    window.endorsement.validated = validated;

    return validated;
};


var endorsementStep = function() {
    var source = $("#endorsed-list").html();
    var template = Handlebars.compile(source);
    var context = {
        endorse_o365: endorseOffice365(),
        endorse_google: endorseGoogle(),
        endorsed: endorseUWNetids(getValidNetidList())
    };

    $('#uwnetids-endorsed').html(template(context));
    showEndorsedStep();
};


var endorseUWNetids = function(to_endorse) {
    var endorsed = [];

    $.each(to_endorse, function (netid, endorsements) {

        /// FAKE WEB SERVICE RESPONSES
        var endorsed_o365 = Math.random() > 0.15;
        var endorsed_google = Math.random() > 0.15;

        $.each(window.endorsement.validated, function () {
            if (this.netid == netid) {
                endorsed.push({
                    netid: netid,
                    name: this.name,
                    endorsement: {
                        o365: {
                            endorsed: endorsements.o365,
                            comment: endorsed_o365 ? '' : 'Some made up reason for failure'
                        },
                        google: {
                            endorsed: endorsements.google,
                            comment: endorsed_google ? '' : 'Some made up reason for failure'
                        }
                    }
                });

                return false;
            }
        });
    });

    return endorsed;
};

var getValidNetidList = function () {
    var to_endorse = {};
    var validated = [];

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
                        }
                    }
                }

                return false;
            }
        });
    });

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
                        }
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
                        to_endorse[this.netid].google = false;
                    } else {
                        to_endorse[this.netid] = {
                            google: true
                        }
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
                if (this.subscription.o365e &&
                    this.subscription.o365.eligible) {
                    if (netid in to_endorse) {
                        to_endorse[this.netid].o365 = false;
                    } else {
                        to_endorse[this.netid] = {
                            o365: true
                        }
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
