// common service endorse javascript

var Endorse = {
    load: function () {
        this._loadContainer();
        this._registerEvents();
    },

    _loadContainer: function () {
        $('#app_content').append($("#endorse_modal_container").html());
    },

    _registerEvents: function () {
        $(document).on('click', 'button#confirm_endorsement_responsibility', function (e) {
            var $button = $(this),
                $rows = $button.data('$rows'),
                to_endorse = {};

            $rows.each(function (i, row) {
                var $row = $(row),
                    netid = $row.attr('data-netid'),
                    netid_name = $row.attr('data-netid-name'),
                    email = EmailEdit.getEditedEmail(netid),
                    service = $row.attr('data-service'),
                    service_name = $row.attr('data-service-name'),
                    reason = Reasons.getReason($row);

                if (!to_endorse.hasOwnProperty(netid)) {
                    to_endorse[netid] = {};
                }

                if (email && email.length) {
                    to_endorse[netid].email = email;
                }

                if (!to_endorse[netid].hasOwnProperty(service)) {
                    to_endorse[netid][service] = {}
                }

                to_endorse[netid][service].state = true;
                to_endorse[netid][service].reason = reason;

                $('.endorse_' + service + '_' + netid, $row).button('loading');
            });

            $button.closest('.modal').modal('hide');
            Endorse._endorseUWNetID(to_endorse, $rows.closest('div.panel'));
        }).on('change', '#endorse_modal input', function () {
            var $accept_button = $(this).closest('#endorse_modal').find('button#confirm_endorsement_responsibility'),
                $checkboxes = $('input.accept_responsibility'),
                checked = 0;

            $checkboxes.each(function () {
                if (this.checked)
                    checked += 1;
            });

            // accept all inputs and no "errors"
            if ($checkboxes.length === checked && $('.error').length === 0) {
                $accept_button.removeAttr('disabled');
            } else {
                $accept_button.attr('disabled', 'disabled');
            }
        });
    },

    endorse: function (modal_content_id, $rows) {
        var $modal = $('#endorse_modal'),
            template = Handlebars.compile($('#' + modal_content_id).html()),
            context = Endorse._endorseModalContext($rows);

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
        $modal.find('button#confirm_endorsement_responsibility').data('$rows', $rows);
    },

    _endorseModalContext: function ($rows) {
        var endorse_o365 = [],
            endorse_google = [],
            context = {
                endorse_o365: [],
                endorse_google: [],
                endorse_netid_count: 0,
                endorse_o365_netid_count: 0,
                endorse_google_netid_count: 0
            };

        $rows.each(function (i, row) {
            var $row = $(row),
                netid = $row.attr('data-netid'),
                netid_name = $row.attr('data-netid-name'),
                email = $row.attr('data-netid-initial-email'),
                service = $row.attr('data-service'),
                service_name = $row.attr('data-service-name');

            if (service === 'o365') {
                context.endorse_o365.push({
                    netid: netid,
                    email: email
                });
            }

            if (service === 'google') {
                context.endorse_google.push({
                    netid: netid,
                    email: email
                });
            }
        });

        context.endorse_o365_netid_count = context.endorse_o365.length;
        context.endorse_google_netid_count = context.endorse_google.length;
        context.endorse_netid_count = context.endorse_google_netid_count + context.endorse_o365_netid_count;
        return context;
    },

    _endorseUWNetID: function(endorsees, $panel) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $.ajax({
            url: "/api/v1/endorse/",
            dataType: "JSON",
            data: JSON.stringify(endorsees),
            type: "POST",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                $panel.trigger('endorse:UWNetIDsEndorseSuccess', [{
                    endorsees: endorsees,
                    endorsed: results
                }]);
            },
            error: function(xhr, status, error) {
                var error_event_id = event_id + 'Error';

                $panel.trigger('endorse:UWNetIDsEndorseError', [error]);
            }
        });
    }
};
