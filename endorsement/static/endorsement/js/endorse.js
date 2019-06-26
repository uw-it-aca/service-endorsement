// common service endorse javascript
/* jshint esversion: 6 */

import { Reasons } from "./reasons.js";
import { EmailEdit } from "./emailedit.js";

var Endorse = (function () {
    var _loadContainer = function () {
        $('#app_content').append($("#endorse_modal_container").html());
    },

    _registerEvents = function () {
        $(document).on('click', 'button#confirm_endorsement_responsibility', function (e) {
            var $button = $(this),
                to_endorse;

            to_endorse = gatherEndorsementsByRow($button.data('$rows'), 'endorse', true, false);
            _endorseUWNetIDs(to_endorse, $button.data('$panel'));
            $button.closest('.modal').modal('hide');
        }).on('change', '#endorse_modal input', function () {
            var $modal = $(this).closest('#endorse_modal'),
                $accept_button = $('button#confirm_endorsement_responsibility', $modal),
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

    _endorseModalContext = function ($rows) {
        var context = {
            unique: [],
            endorse_o365: [],
            endorse_google: [],
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

            if (context.unique.indexOf(netid) < 0) {
                context.unique.push(netid);
            }

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
        return context;
    },

    _endorseUWNetIDs = function(endorsees, $panel) {
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
    };

    // Exported functions
    var load = function () {
            _loadContainer();
            _registerEvents();
        },
        
        endorse = function (modal_content_id, $rows) {
            var $modal = $('#endorse_modal'),
                template = Handlebars.compile($('#' + modal_content_id).html()),
                context = _endorseModalContext($rows);

            $('.modal-content', $modal).html(template(context));
            $modal.modal('show');
            $modal.find('button#confirm_endorsement_responsibility')
                .data('$rows', $rows)
                .data('$panel', $rows.closest('div.panel'));
        },

        gatherEndorsementsByRow = function ($rows, action, state, store) {
            var collection = {
            };

            $rows.each(function (i, row) {
                var $row = $(row),
                    netid = $row.attr('data-netid'),
                    netid_name = $row.attr('data-netid-name'),
                    email = EmailEdit.getEditedEmail(netid),
                    service = $row.attr('data-service'),
                    service_name = $row.attr('data-service-name'),
                    reason = Reasons.getReason($row);

                if (!collection.hasOwnProperty(netid)) {
                    collection[netid] = {};
                }

                if (email && email.length) {
                    collection[netid].email = email;
                }

                if (!collection[netid].hasOwnProperty(service)) {
                    collection[netid][service] = {};
                }

                if (store || $row.attr('data-netid-type') !== undefined) {
                    collection[netid].store = true;
                }

                collection[netid][service].state = state;
                collection[netid][service].reason = reason;

                $('.' + action + '_' + service + '_' + netid, $row).button('loading');
            });

            return collection;
        },

        updateEndorsementForRowContext = function (endorsement) {
            if (endorsement.hasOwnProperty('endorsers')) {
                var remove = -1;

                $.each(endorsement.endorsers, function (i, endorser) {
                    if (endorser.netid === window.user.netid) {
                        remove = i;
                        return false;
                    }
                });

                if (remove >= 0) {
                    endorsement.endorsers.splice(remove, 1);
                }
            }

            if (endorsement.hasOwnProperty('datetime_endorsed')) {
                var now = moment(),
                    provisioned = moment(endorsement.datetime_endorsed),
                    expires = moment(endorsement.datetime_endorsed).add(365, 'days'),
                    expiring = moment(endorsement.datetime_endorsed).add(30, 'days');

                endorsement.expires = expires.format('M/D/YYYY');
                endorsement.expires_relative = expires.fromNow();

                if (now.isBetween(expiring, expires)) {
                    endorsement.expiring = endorsement.expires;
                }

                if (now.isAfter(expires)) {
                    endorsement.expired = endorsement.expires;
                }
            }
        },

        updateEndorsementRows = function (endorsements) {
            var row_source = $('#endorsee-row').html(),
                row_template = Handlebars.compile(row_source);

            $.each(endorsements, function (netid, data) {
                if (data.error) {
                    Notify.error('Error provisioning netid "' + netid + '"');
                    $('button.endorse_service', $('tr[data-netid="' + netid + '"]')).button('reset');
                    return true;
                }

                $.each(data.endorsements, function (service, endorsement) {
                    var $row = $('tr[data-netid="' + netid + '"][data-service="' + service + '"]'),
                        type,
                        context;

                    if ($row.length === 0) {
                        return true;
                    }

                    updateEndorsementForRowContext(endorsement);

                    context = {
                        netid: netid,
                        name: data.name ? data.name : $row.attr('data-netid-name'),
                        email: data.email ? data.email : $row.attr('data-netid-initial-email'),
                        service: service,
                        endorsement: endorsement
                    };

                    type = $row.attr('data-netid-type');
                    if (type) {
                        context.type = type;
                    }

                    $row.replaceWith(row_template(context));
                });
            });

            updateExpireWarning();
        },

        updateExpireWarning = function () {
            if ($('.expiring-service').length > 0) {
                $('.expiring_netids').removeClass('visually-hidden');

            } else {
                $('.expiring_netids').addClass('visually-hidden');
            }
        };

    return {
        load: load,
        endorse: endorse,
        gatherEndorsementsByRow: gatherEndorsementsByRow,
        updateEndorsementForRowContext: updateEndorsementForRowContext,
        updateEndorsementRows: updateEndorsementRows,
        updateExpireWarning: updateExpireWarning
    };
}());

export { Endorse };
