Handlebars.registerPartial('validation_partial', $("#validation_partial").html());
Handlebars.registerPartial('endorsed_partial', $("#endorsed-partial").html());

Handlebars.registerHelper('endorsable', function(o365, google) {
    if ((o365 && this.endorsement.o365.eligible) ||
        (google && this.endorsement.google.eligible)) {
        return 'checked="checked"';
    } else {
        return 'disabled="1"';
    }
});

Handlebars.registerHelper('revokable', function(o365, google) {
    if ((o365 && this.endorsement.o365.eligible) ||
        (google && this.endorsement.google.eligible)) {
        return 'checked="checked"';
    } else {
        return 'disabled="1"';
    }
});


Handlebars.registerHelper('subscription_context', function(context, netid, endorsable, revokable, svc) {
    var new_context = context;
    new_context.netid = netid;
    new_context.endorsable = endorsable;
    new_context.revokable = revokable;
    new_context.svc = svc;
    return new_context;
});
