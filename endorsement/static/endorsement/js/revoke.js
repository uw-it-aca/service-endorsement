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
        $(document).on('click', 'button#revoke', function (e) {
            var $this = $(this),
                netid = $this.attr('data-netid'),
                service = $this.attr('data-service'),
                event_id = $this.attr('data-event-id'),
                to_revoke = {},
                $button = $('button[data-netid="' + netid + '"][data-service="' + service + '"]'),
                $panel = $button.parents('.panel');

            $this.parents('.modal').modal('hide');
            $button.button('loading');
            to_revoke[netid] = {};
            to_revoke[netid][service] = false;
            Revoke._revokeUWNetIDs(to_revoke, event_id, $panel);
        });
    },

    revoke: function (content_id, $row, event_id) {
        var $modal = $('#revoke_modal');

        $('.modal-content', $modal).html(
            Handlebars.compile($(content_id).html())({
                netid: $row.attr('data-netid'),
                service: $row.attr('data-service'),
                service_name: $row.attr('data-service-name'),
                event_id: event_id
            }));

        $modal.modal('show');
    },

    _revokeUWNetIDs: function(revokees, event_id, $panel) {
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
                $panel.trigger(event_id, [{
                    revokees: revokees,
                    revoked: results
                }]);
            },
            error: function(xhr, status, error) {
                var error_event_id = event_id + 'Error';

                $panel.trigger(error_event_id, [error]);
            }
        });
    }
};
