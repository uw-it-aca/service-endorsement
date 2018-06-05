Handlebars.registerPartial('validation_partial', $("#validation_partial").html());
Handlebars.registerPartial('endorsed_partial', $("#endorsed-partial").html());
Handlebars.registerPartial('reasons_partial', $("#reasons_partial").html());
Handlebars.registerPartial('endorsers_partial', $("#endorsers_partial").html());
Handlebars.registerPartial('endorse_button_partial', $("#endorse_button_partial").html());

Handlebars.registerHelper('endorsable', function(o365, google) {
    if ((o365 && this.o365.eligible) ||
        (google && this.google.eligible)) {
        return 'checked="checked"';
    } else {
        return 'disabled="1"';
    }
});

Handlebars.registerHelper('unendorsed', function(endorsements, options) {
    return !(endorsements &&
            ((endorsements.o365 && endorsements.o365.datetime_endorsed != null) &&
             (endorsements.google && endorsements.google.datetime_endorsed != null)))
        ? options.fn(this) : options.inverse(this);
});

Handlebars.registerHelper('reason', function(endorsements, reason, options) {
    return (endorsements &&
            ((endorsements.o365 && endorsements.o365.reason === reason) ||
             (endorsements.google && endorsements.google.reason === reason)))
        ? options.fn(this) : options.inverse(this);
});

Handlebars.registerHelper('has_reason', function(endorsements, options) {
    return (!(endorsements &&
              ((endorsements.o365 && endorsements.o365.reason.length) ||
               (endorsements.google && endorsements.google.reason.length))))
        ? options.fn(this) : options.inverse(this);
});

Handlebars.registerHelper('revokable', function(o365, google) {
    if ((o365 && this.o365.eligible) ||
        (google && this.google.eligible)) {
        return 'checked="checked"';
    } else {
        return 'disabled="1"';
    }
});

Handlebars.registerHelper('subscription_context', function(context, netid, svc) {
    var new_context = context;
    new_context.netid = netid;
    new_context.svc = svc;
    return new_context;
});

Handlebars.registerHelper('plural', function(n, singular, plural) {
    if (n === 1) { 
        return singular;
    }

    return plural;
});

Handlebars.registerHelper('equals', function(a, b, options) {
    return (a == b) ? options.fn(this) : options.inverse(this);
});
