$(window.document).ready(function() {
    Handlebars.registerPartial({
        'validation_partial':  $("#validation_partial").html(),
        'reasons_partial': $("#reasons_partial").html(),
        'endorsement_row_partial': $("#endorsement_row_partial").html(),
        'endorse_button_partial': $("#endorse_button_partial").html(),
        'display_filter_partial': $("#display_filter_partial").html(),
        'email_editor_partial': $("#email_editor_partial").html(),
        'office_access_row_partial': $("#office_access_row_partial").html(),
        'office_conflict_row_partial': $('#office_conflict_row_partial').html(),
        'modal_action_partial': $("#modal_action_partial_template").html(),
        'shared_drives_row_partial': $("#shared_drives_row_partial").html(),

    });

    Handlebars.registerHelper({
        'plural': function(n, singular, plural) {
            if (n === 1) {
                return singular;
            }

            return plural;
        },
        'slice': function(a, start, end, options) {
            if(!a || a.length == 0)
                return options.inverse(this);

            var result = [];
            for(var i = start; i < end && i < a.length; ++i)
                result.push(options.fn(a[i]));

            return result.join('');
        },
        'even': function(n) { return ((n % 2) === 0); },
        'eq': function(a, b) { return (a === b); },
        'gt': function(a, b) { return (a > b); },
        'lte': function(a, b) { return (a <= b); },
        'and': function(a, b) { return (a && b); },
        'or': function(a, b) { return (a || b); },
        'not': function(a) { return (!a); },
        'numberFormat': function(n) { return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","); },
        'driveCapacity': function(n) { return (n < 1) ? Math.round(n * 1000) + 'MB' : (n > 1000) ? (n/1000) + 'TB' : n + 'GB'; },
    });
});
