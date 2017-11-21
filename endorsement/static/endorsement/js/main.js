// javascript for service endorsement manager

$(window.document).ready(function() {
	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();
    enableCheckEligibility();

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
    });

    $('#app_content').on('change', '#endorse_o365, #endorse_google, #netid_list',  function(e) {
        enableCheckEligibility();
    });

    $('#app_content').on('keypress', '#netid_list', function () {
        enableCheckEligibility();
    });

});

var enableCheckEligibility = function() {
    var netids = getNetidList();

    if (netids.length > 0 && (endorseOffice365() || endorseGoogle())) {
        $('#validate').removeAttr('disabled');
    } else {
        $('#validate').attr('disabled', 'disabled');
    }
}

var endorseGoogle = function () {
    return $("#endorse_google").is(':checked');
}

var endorseOffice365 = function () {
    return $("#endorse_o365").is(':checked');
}

var displayPageHeader = function() {
    var source = $("#page-top").html();
    var template = Handlebars.compile(source);
    $("#top_banner").html(template({
        netid: window.user.netid
    }));
}

var validationStep = function() {
    var source = $("#validated-list").html();
    var template = Handlebars.compile(source);
    var $endorsement_group = $('.endorsement-group input[type="checkbox"]');
    var context = {
        endorse_o365: endorseOffice365(),
        endorse_google: endorseGoogle(),
        netids: validateUWNetids(getNetidList())
    }

    $('#uwnetids-validated').html(template(context));
        
    $endorsement_group.attr('disabled', true);
    showValidationStep();
}


var validateUWNetids = function(netids) {
    var validated = [];

    $.each(netids, function (i, netid) {


        /// FAKE WEB SERVICE RESPONSES
        var can_o365 = Math.random() > .3;
        var can_google = Math.random() > .3;
        var valid_netid = Math.random() > .15;
        var do_comment = Math.random() < .25;




        validated.push({
            netid: netid,
            valid_netid: valid_netid,
            name: netid + '. Lastname',
            email: netid + '@uw.edu',
            endorsement: {
                google: {
                    eligible: can_google,
                    comment: can_google ? (do_comment ? 'already endorsed by mumble': null): "not a valid netid"
                },
                o365: {
                    eligible: can_o365,
                    comment: can_o365 ? (do_comment ? 'already endorsed by mumble': null): "not a valid netid"
                }
            }
        });
    });

    window.endorsement = {};
    window.endorsement.validated = validated;

    return validated;
}


var endorsementStep = function() {
    var source = $("#endorsed-list").html();
    var template = Handlebars.compile(source);
    var context = {
        endorse_o365: endorseOffice365(),
        endorse_google: endorseGoogle(),
        endorsed: endorseUWNetids(getValidNetidList())
    }

    $('#uwnetids-endorsed').html(template(context));
    showEndorsedStep();
}


var endorseUWNetids = function(to_endorse) {
    var endorsed = [];

    $.each(to_endorse, function (i, endorsee) {

        /// FAKE WEB SERVICE RESPONSES
        var endorsed_o365 = Math.random() > .25;
        var endorsed_google = Math.random() > .25;
        var do_comment = Math.random() < .25;



        $.each(window.endorsement.validated, function () {
            if (this.netid == endorsee.netid) {
                endorsed.push({
                    netid: endorsee.netid,
                    name: this.name,
                    endorsement: {
                        o365: {
                            endorsed: endorsed_o365,
                            comment: endorsed_o365 ? '' : 'Endorsement Failed'
                        },
                        google: {
                            endorsed: endorsed_google,
                            comment: endorsed_google ? '' : 'Endorsement Failed'
                        }
                    }
                })

                return false;
            }
        });
    });

    return endorsed;
}

var getValidNetidList = function () {
    var to_endorse = [];
    var validated = [];

    $('input[name="picked"]:checked').each(function (e) {
        validated.push($(this).val());
    });

    $.each(window.endorsement.validated, function () {
        if (validated.indexOf(this.netid) >= 0) {
            var endorsement = {
                netid: this.netid,
                service: {}
            };

            if (this.endorsement.o365 &&
                this.endorsement.google.eligible) {
                endorsement.service.o365 = true;
            }

            if (this.endorsement.google &&
                this.endorsement.google.eligible) {
                endorsement.service.google = true;
            }

            to_endorse.push(endorsement);
        }
    });

    return to_endorse;
}


var showInputStep = function () {
    $('.endorsement-group input').removeAttr('disabled');
    $(['input.endorse_o365', 'input.endorse_google'])
    $('#uwnetids-validated').hide();
    $('#uwnetids-endorsed').hide();
    $('#uwnetids-input').show();
}

var showValidationStep = function () {
    $('.endorsement-group input').attr('disabled', true);
    $('#uwnetids-input').hide();
    $('#uwnetids-endorsed').hide();
    $('#uwnetids-validated').show();
}

var showEndorsedStep = function () {
    $('.endorsement-group input').attr('disabled', true);
    $('#uwnetids-input').hide();
    $('#uwnetids-validated').hide();
    $('#uwnetids-endorsed').show();
}

var getNetidList = function () {
    return unique($('#netid_list').val().replace(/\n/g, ' ').split(/[ ,]+/))
}

var unique = function(array) {
    return $.grep(array, function(el, i) {
        return el.length > 0 && i === $.inArray(el, array);
    });
}
