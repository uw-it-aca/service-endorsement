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
        'even': (n) => (n % 2) === 0,
        'eq': (a, b) => a === b,
        'gt': (a, b) => a > b,
        'lte': (a, b) => a <= b,
        'and': (a, b) => a && b,
        'or': (a, b) => a || b,
        'not': (a) => !a
    });
});
