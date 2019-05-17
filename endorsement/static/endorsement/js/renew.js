// common service endorsement renewal javascript

var Renew = {
    load: function () {
        this._loadContainer();
        this._registerEvents();
    },

    _loadContainer: function () {
        $('#app_content').append($("#renew_modal_container").html());
    },

    _registerEvents: function () {
        $(document).on('click', 'button#confirm_renew_responsibility', function (e) {
            var $button = $(this),
                to_renew;

            to_renew = Renew._gatherRenewals($button.data('$rows'));
            Renew._renewUWNetID(to_renew, $button.data('$panel'));
            $button.closest('.modal').modal('hide');
        }).on('change', '#renew_modal input', function () {
            var $modal = $(this).closest('#renew_modal'),
                $accept_button = $('button#confirm_renew_responsibility', $modal),
                $checkboxes = $('input.accept_responsibility', $modal),
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

    renew: function (modal_content_id, $rows) {
        var $modal = $('#renew_modal'),
            template = Handlebars.compile($('#' + modal_content_id).html()),
            context = Renew._renewModalContext($rows);

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
        $modal.find('button#confirm_renew_responsibility')
            .data('$rows', $rows)
            .data('$panel', $rows.closest('div.panel'));
    },

    _renewModalContext: function ($rows) {
        var renew_o365 = [],
            renew_google = [],
            context = {
                renew_o365: [],
                renew_google: [],
                renew_netid_count: 0,
                renew_o365_netid_count: 0,
                renew_google_netid_count: 0
            };

        $rows.each(function (i, row) {
            var $row = $(row),
                netid = $row.attr('data-netid'),
                netid_name = $row.attr('data-netid-name'),
                email = $row.attr('data-netid-initial-email'),
                service = $row.attr('data-service'),
                service_name = $row.attr('data-service-name');

            if (service === 'o365') {
                context.renew_o365.push({
                    netid: netid,
                    email: email
                });
            }

            if (service === 'google') {
                context.renew_google.push({
                    netid: netid,
                    email: email
                });
            }
        });

        context.renew_o365_netid_count = context.renew_o365.length;
        context.renew_google_netid_count = context.renew_google.length;
        context.renew_netid_count = context.renew_google_netid_count + context.renew_o365_netid_count;
        return context;
    },

    _gatherRenewals: function ($rows) {
        to_renew = {};

        $rows.each(function (i, row) {
            var $row = $(row),
                netid = $row.attr('data-netid'),
                netid_name = $row.attr('data-netid-name'),
                email = EmailEdit.getEditedEmail(netid),
                service = $row.attr('data-service'),
                service_name = $row.attr('data-service-name'),
                store = ($row.attr('data-netid-type') !== undefined),
                reason = Reasons.getReason($row);

            if (!to_renew.hasOwnProperty(netid)) {
                to_renew[netid] = {};
            }

            if (email && email.length) {
                to_renew[netid].email = email;
            }

            if (!to_renew[netid].hasOwnProperty(service)) {
                to_renew[netid][service] = {}
            }

            if (store) {
                to_renew[netid].store = true;
            }

            to_renew[netid][service].state = true;
            to_renew[netid][service].reason = reason;

            $('.renew_' + service + '_' + netid, $row).button('loading');
        });

        return to_renew;
    },

    _renewUWNetID: function(renewees, $panel) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $(document).trigger('endorse:UWNetIDsRenewStart', [renewees]);

        $.ajax({
            url: "/api/v1/endorse/",
            dataType: "JSON",
            data: JSON.stringify(renewees),
            type: "POST",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                $panel.trigger('endorse:UWNetIDsRenewSuccess', [{
                    endorsees: renewees,
                    endorsed: results
                }]);
            },
            error: function(xhr, status, error) {
                $panel.trigger('endorse:UWNetIDsRenewError', [error]);
            }
        });
    }
};
