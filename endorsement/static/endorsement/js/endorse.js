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
        $(document).on('click', 'button#endorse', function (e) {
            var $this = $(this),
                netid = $this.attr('data-netid'),
                service = $this.attr('data-service'),
                event_id = $this.attr('data-event-id'),
                to_endorse = {},
                $button = $('button[data-netid="' + netid + '"][data-service="' + service + '"]'),
                $panel = $button.parents('.panel');

            $this.parents('.modal').modal('hide');
            $button.button('loading');
            to_endorse[netid] = {};
            to_endorse[netid][service] = true;
            Endorse._endorseUWNetID(to_endorse, event_id, $panel);
        });
    },

    endorse: function ($button, content_id, event_id) {
        var $modal = $('#endorse_modal');

        $('.modal-content', $modal).html(
            Handlebars.compile($(content_id).html())({
                netid: $button.attr('data-netid'),
                service: $button.attr('data-service'),
                service_name: $button.attr('data-service-name'),
                event_id: event_id
            }));

        $modal.modal('show');
    },

    _endorseUWNetID: function(endorsees, event_id, $panel) {
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
                $panel.trigger(event_id, [{
                    endorsees: endorsees,
                    endorseded: results
                }]);
            },
            error: function(xhr, status, error) {
                var error_event_id = event_id + 'Error';

                $panel.trigger(error_event_id, [error]);
            }
        });
    }
};
