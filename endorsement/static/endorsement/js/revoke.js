// common service revocation javascript

var Revoke = {
    load: function () {
        this._loadContainer();
        this._registerEvents();
    },

    _loadContainer: function () {
        $('#app_content').append($("#revoke_modal_container").html());
    },

    _registerEvents: function () {
        $(document).on('click', 'button#confirm_revoke', function (e) {
            var $button = $(this),
                to_revoke;

            to_revoke = Revoke._gatherRevocations($button.data('$rows'));
            Revoke._revokeUWNetIDs(to_revoke, $button.data('$panel'));
            $button.closest('.modal').modal('hide');
        });
    },

    revoke: function (modal_content_id, $rows) {
        var $modal = $('#revoke_modal'),
            template = Handlebars.compile($('#' + modal_content_id).html()),
            context = Revoke._revokeModalContext($rows);

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
        $modal.find('button#confirm_revoke')
            .data('$rows', $rows)
            .data('$panel', $rows.closest('div.panel'));
    },

    _revokeModalContext: function ($rows) {
        var revoke_o365 = [],
            revoke_google = [],
            context = {
                revoke_o365: [],
                revoke_google: [],
                revoke_netid_count: 0,
                revoke_o365_netid_count: 0,
                revoke_google_netid_count: 0
            };

        $rows.each(function (i, row) {
            var $row = $(row),
                netid = $row.attr('data-netid'),
                netid_name = $row.attr('data-netid-name'),
                email = $row.attr('data-netid-initial-email'),
                service = $row.attr('data-service'),
                service_name = $row.attr('data-service-name');

            if (service === 'o365') {
                context.revoke_o365.push({
                    netid: netid,
                    email: email
                });
            }

            if (service === 'google') {
                context.revoke_google.push({
                    netid: netid,
                    email: email
                });
            }
        });

        context.revoke_o365_netid_count = context.revoke_o365.length;
        context.revoke_google_netid_count = context.revoke_google.length;
        context.revoke_netid_count = context.revoke_google_netid_count + context.revoke_o365_netid_count;
        return context;
    },

    _gatherRevocations: function ($rows) {
        var to_revoke = {};

        $rows.each(function (i, row) {
            var $row = $(row),
                netid = $row.attr('data-netid'),
                netid_name = $row.attr('data-netid-name'),
                email = EmailEdit.getEditedEmail(netid),
                service = $row.attr('data-service'),
                service_name = $row.attr('data-service-name'),
                store = ($row.attr('data-netid-type') !== undefined),
                reason = Reasons.getReason($row);

            if (!to_revoke.hasOwnProperty(netid)) {
                to_revoke[netid] = {};
            }

            if (email && email.length) {
                to_revoke[netid].email = email;
            }

            if (!to_revoke[netid].hasOwnProperty(service)) {
                to_revoke[netid][service] = {}
            }

            if (store) {
                to_revoke[netid].store = true;
            }

            to_revoke[netid][service].state = false;
            to_revoke[netid][service].reason = reason;

            $('.revoke_' + service + '_' + netid, $row).button('loading');
        });

        return to_revoke;
    },

    _revokeUWNetIDs: function(revokees, $panel) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $.ajax({
            url: "/api/v1/endorse/",
            dataType: "JSON",
            data: JSON.stringify(revokees),
            type: "POST",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                $panel.trigger('endorse:UWNetIDsRevokeSuccess', [{
                    revokees: revokees,
                    revoked: results
                }]);
            },
            error: function(xhr, status, error) {
                var error_event_id = event_id + 'Error';

                $panel.trigger('endorse:UWNetIDsRevokeError', [error]);
            }
        });
    }
};
