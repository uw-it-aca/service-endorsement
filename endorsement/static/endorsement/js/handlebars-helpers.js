Handlebars.registerHelper('checked_or_disabled', function(o365, google) {
    if ((o365 && this.endorsement.o365.eligible) ||
        (google && this.endorsement.google.eligible)) {
        return 'checked="checked"';
    } else {
        return 'disabled="1"';
    }
});


Handlebars.registerHelper('invalid_netid_columns', function(netid_obj, o365, google) {
    n = 4;
    if (o365 && netid_obj.endorsement.o365.eligible) {
        n += 1;
    }

    if (google && netid_obj.endorsement.google.eligible) {
        n += 1;
    }

    return n;
});
