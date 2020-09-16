$(window.document).ready(function() {

    Handlebars.registerPartial({
        'validation_partial':  $("#validation_partial").html(),
        'reasons_partial': $("#reasons_partial").html(),
        'endorsement_row_partial': $("#endorsement_row_partial").html(),
        'endorse_button_partial': $("#endorse_button_partial").html(),
        'display_filter_partial': $("#display_filter_partial").html(),
        'email_editor_partial': $("#email_editor_partial").html()
    });

    Handlebars.registerHelper({
        'endorsable': function(o365, google) {
            if ((o365 && this.o365.eligible) ||
                (google && this.google.eligible)) {
                return 'checked="checked"';
            } else {
                return 'disabled="1"';
            }
        },
        'endorsed': function(endorsements, options) {
            return (endorsements &&
                    ((endorsements.o365 && endorsements.o365.datetime_endorsed !== null) ||
                     (endorsements.google && endorsements.google.datetime_endorsed !== null))) ? options.fn(this) : options.inverse(this);
        },
        'reason': function(endorsements, reason, options) {
            if (endorsements) {
                if (endorsements.o365 && endorsements.o365.reason) {
                    return endorsements.o365.reason;
                } else if (endorsements.google && endorsements.google.reason) {
                    return endorsements.google.reason;
                }
            }

            return "";
        },
        'has_reason': function(endorsements, options) {
            return (!(endorsements &&
                      ((endorsements.o365 && endorsements.o365.reason.length) ||
                       (endorsements.google && endorsements.google.reason.length)))) ? options.fn(this) : options.inverse(this);
        },
        'revokable': function(o365, google) {
            if ((o365 && this.o365.eligible) ||
                (google && this.google.eligible)) {
                return 'checked="checked"';
            } else {
                return 'disabled="1"';
            }
        },
        'subscription_context': function(context, netid, svc) {
            var new_context = context;
            new_context.netid = netid;
            new_context.svc = svc;
            return new_context;
        },
        'plural': function(n, singular, plural) {
            if (n === 1) { 
                return singular;
            }

            return plural;
        },
        'single_endorsement': function(o365, google, options) {
            if (o365 && Object.keys(o365).length === 1 &&
                google && Object.keys(google).length === 1 &&
                o365[Object.keys(o365)[0]] === google[Object.keys(google)[0]]) {
                return options.fn(this);
            }

            return options.inverse(this);
        },
        'equals': function(a, b, options) {
            return (a == b) ? options.fn(this) : options.inverse(this);
        },
        'gt': function(a, b, options) {
            return (a > b) ? options.fn(this) : options.inverse(this);
        },
        'ifAndNot': function(a, b, options) {
            return (a && !b) ? options.fn(this) : options.inverse(this);
        }
    });
});
