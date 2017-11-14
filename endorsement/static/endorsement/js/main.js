// javascript for service endorsement manager

$(window.document).ready(function() {
	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();
    enableCheckEligibility();

    $('#validate').on('click', function(e) {
        validationStep();
    });

    $('#endorse_o365, #endorse_google, #netidlist').on('change', function () {
        enableCheckEligibility();
    });

    $('#netidlist').on('keypress', function () {
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
    var $validated = $('#uwnetids-validated');
    var source = $("#validated-list").html();
    var template = Handlebars.compile(source);
    var $endorsement_group = $('.endorsement-group input[type="checkbox"]');
    var context = {
        endorse_o365: endorseOffice365(),
        endorse_google: endorseGoogle(),
        netids: validateUWNetids(getNetidList())
    }

    $validated.html(template(context));
        
    $('#netid_input').on('click', function(e) {
        var $validated = $('#uwnetids-validated');

        $(['input.endorse_o365', 'input.endorse_google']).removeAttr('disabled');
        $endorsement_group.removeAttr('disabled');
        $validated.hide();
        $('#uwnetids').show();
    });

    $('#uwnetids').hide();
    $endorsement_group.attr('disabled', true);
    $validated.show();
}


var validateUWNetids = function(netids) {
    var validated = [];

    $.each(netids, function () {
        var netid = this;




        /// FAKE WEB SERVICE RESPONSES
        var can_o365 = Math.random() > .6;
        var can_google = Math.random() > .6;
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

    return validated;
}


var getNetidList = function () {
    return unique($('#netidlist').val().replace(/\n/g, ' ').split(/[ ,]+/))
}


var unique = function(array) {
    return $.grep(array, function(el, i) {
        return el.length > 0 && i === $.inArray(el, array);
    });
}
