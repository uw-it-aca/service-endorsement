// common service revocation javascript
/* jshint esversion: 6 */

import { Endorse } from "./endorse.js";

var Revoke = (function () {
    var _loadContainer = function () {
        $('#app_content').append($("#revoke_modal_container").html());
    },

    _registerEvents = function () {
        $(document).on('click', 'button#confirm_revoke', function (e) {
            var $button = $(this),
                to_revoke;

            to_revoke = Endorse.gatherEndorsementsByRow($button.data('$rows'), 'revoke', false, true);
            _revokeUWNetIDs(to_revoke, $button.data('$panel'));
            $button.closest('.modal').modal('hide');
        });
    },

    _successModal = function (revoked) {
        var source = $("#revoke_success_modal_content").html(),
            template = Handlebars.compile(source),
            $modal = $('#revoke_success_modal');

        $('.modal-content', $modal).html(template());
        $modal.modal('show');
    },

    _revokeModalContext = function ($rows) {
        var context = {
                unique: [],
                services: {}
            };

        $.each(window.endorsed_services, function(k, v) {
            context.services[k] = {
                'name': v.category_name,
                'revoke': []
            };
        });

        $rows.each(function (i, row) {
            var $row = $(row),
                netid = $row.attr('data-netid'),
                netid_name = $row.attr('data-netid-name'),
                email = $row.attr('data-netid-initial-email'),
                service = $row.attr('data-service'),
                service_name = $row.attr('data-service-name');

            if (context.unique.indexOf(netid) < 0) {
                context.unique.push(netid);
            }

            if (context.services.hasOwnProperty(service)) {
                context.services[service].revoke.push({
                    netid: netid,
                    email: email
                });
            }
        });

        context.netid_count = context.unique.length;

        $.each(context.services, function(k) {
            context.services[k].count = context.services[k].revoke.length;
        });

        return context;
    },

    _revokeUWNetIDs = function(revokees, $panel) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $.ajax({
            url: "/api/v1/endorse/",
            type: "POST",
            data: JSON.stringify({'endorsees': revokees }),
            contentType: "application/json",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                // pause for renew modal fade
                if (results.endorsed) {
                    setTimeout(function () {
                        _successModal(results.endorsed);
                    }, 500);
                }

                $panel.trigger('endorse:UWNetIDsRevokeSuccess', [{
                    revokees: revokees,
                    revoked: results
                }]);
            },
            error: function(xhr, status, error) {
                $panel.trigger('endorse:UWNetIDsRevokeError', [revokees, error]);
            }
        });
    };

    return {
        load: function () {
            _loadContainer();
            _registerEvents();
        },
        revoke: function ($rows) {
            var $modal = $('#revoke_modal'),
                template = Handlebars.compile($('#revoke_modal_content').html()),
                context = _revokeModalContext($rows);

            $('.modal-content', $modal).html(template(context));
            $modal.modal('show');
            $modal.find('button#confirm_revoke')
                .data('$rows', $rows)
                .data('$panel', $rows.closest('div.netid-panel'));
        },
        resetRevokeButton: function (revokees) {
            Endorse.resetActionButton('revoke', revokees);
        }
    };
}());

export { Revoke };
