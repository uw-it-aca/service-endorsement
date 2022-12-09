$(window.document).ready(function() {
    Handlebars.registerPartial({
        'validation_partial':  $("#validation_partial").html(),
        'reasons_partial': $("#reasons_partial").html(),
        'endorsement_row_partial': $("#endorsement_row_partial").html(),
        'endorse_button_partial': $("#endorse_button_partial").html(),
        'display_filter_partial': $("#display_filter_partial").html(),
        'email_editor_partial': $("#email_editor_partial").html(),
        'office_access_row_partial': $("#office_access_row_partial").html(),
        'modal_action_partial': $("#modal_action_partial_template").html()
    });

    Handlebars.registerHelper({
        'plural': function(n, singular, plural) {
            if (n === 1) {
                return singular;
            }

            return plural;
        },
        'equals': function(a, b, options) {
            return (a == b) ? options.fn(this) : options.inverse(this);
        },
        'gt': function(a, b, options) {
            return (a > b) ? options.fn(this) : options.inverse(this);
        },
        'even': function(n, options) {
            return ((n % 2) === 0) ? options.fn(this) : options.inverse(this);
        },
        'ifAndNot': function(a, b, options) {
            return (a && !b) ? options.fn(this) : options.inverse(this);
        }
    });
});
