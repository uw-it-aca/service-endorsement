// common service endorse javascript
/* jshint esversion: 6 */

import { Reasons } from "./reasons.js";
import { EmailEdit } from "./emailedit.js";
import { Notify } from "./notify.js";
import { Banner } from "./banner.js";

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
        }).on('click', '.expiring_netids button.close', function (e) {
            // make sure it stays hidden
            $('.expiring_netids').hide();
        });
    },

    _endorseModalContext = function ($rows) {
        var context = {
            unique: [],
            services: {}
        };

        $.each(window.endorsed_services, function(k, v) {
            context.services[k] = {
                'name': v.category_name,
                'endorsed': []
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

            context.services[service].endorsed.push({
                netid: netid,
                email: email
            });
        });

        context.netid_count = context.unique.length;

        $.each(context.services, function(k) {
            context.services[k].count = context.services[k].endorsed.length;
        });

        return context;
    },

    _endorseUWNetIDs = function(endorsees, $panel) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $.ajax({
            url: "/api/v1/endorse/",
            type: "POST",
            data: JSON.stringify({ "endorsees": endorsees }),
            contentType: "application/json",
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
                $panel.trigger('endorse:UWNetIDsEndorseError', [endorsees, error]);
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
                .data('$panel', $rows.closest('div.netid-panel'));
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

            if (endorsement.hasOwnProperty('datetime_endorsed') && endorsement.datetime_endorsed) {
                var now = moment.utc(),
                    provisioned = moment(endorsement.datetime_endorsed),
                    expiring,
                    expires;

                if (endorsement.datetime_notice_1_emailed) {
                    expiring = moment(endorsement.datetime_notice_1_emailed);
                    expires = moment(endorsement.datetime_notice_1_emailed).add(90, 'days');
               } else {
                    expiring = moment(endorsement.datetime_endorsed).add(275, 'days');
                    expires = moment(endorsement.datetime_endorsed).add(365, 'days');
                }

                endorsement.expires = expires.format('M/D/YYYY');
                endorsement.expires_relative = expires.fromNow();

                if (now.isBetween(expiring, expires, null, '[)')) {
                    endorsement.expiring = endorsement.expires;
                }

                if (now.isAfter(expires)) {
                    endorsement.expired = endorsement.expires;
                }
            }
        },

        updateEndorsementRows = function (endorsements) {
            var row_source = $('#endorsee-row').html(),
                row_template = Handlebars.compile(row_source),
                endorsee_index = 0;

            $.each(endorsements, function (netid, data) {
                var endorsement_index = 0;

                if (data.error) {
                    Notify.error('Error provisioning netid "' + netid + '"');
                    $('button.endorse_service', $('tr[data-netid="' + netid + '"]')).button('reset');
                    return true;
                }

                $.each(data.endorsements, function (service, endorsement) {
                    var $row = $('tr[data-netid="' + netid + '"][data-service="' + service + '"]'),
                        is_first,
                        is_even,
                        type,
                        context;

                    if ($row.length === 0) {
                        return true;
                    }

                    is_first = $row.hasClass('endorsement_row_first');
                    is_even = $row.hasClass('endorsee_row_even');

                    if (endorsement.hasOwnProperty('error')) {
                        Notify.error('Error provisioning <b>' + netid + '</b> for <b>' + endorsement.category_name + '</b>');
                    }

                    updateEndorsementForRowContext(endorsement);

                    context = {
                        netid: netid,
                        name: data.name ? data.name : $row.attr('data-netid-name'),
                        email: data.email ? data.email : $row.attr('data-netid-initial-email'),
                        service: service,
                        endorsement: endorsement,
                        endorsee_index: endorsee_index,
                        endorsement_index: endorsement_index
                    };

                    type = $row.attr('data-netid-type');
                    if (type) {
                        context.type = type;
                    }

                    $row.replaceWith(row_template(context));

                    // restore relative placement
                    $('tr[data-netid="' + netid + '"][data-service="' + service + '"]')
                        .removeClass('endorsement_row_first endorsement_row_following' +
                                     ' endorsee_row_even endorsee_row_odd' +
                                     ' top-border hidden-names')
                        .addClass('endorsement_row_' +
                                  (is_first ? 'first top-border' : 'following hidden-names') +
                                  ' endorsee_row_' + (is_even ? 'even' : 'odd'));

                    endorsement_index += 1;
                });

                endorsee_index += 1;
                endorsement_index = 0;
            });

            updateExpireWarning();
        },

        updateExpireWarning = function () {
            if ($('.expiring-service').length > 0) {
                Banner.renderMessages({
                    'info': [{
                        'hash': 'xxxx',
                        'message': $('#expiring_message').html()
                    }]
                });
            } else {
                Banner.removeMessage('warning', 'xxxx');
            }
        },

        resetActionButton = function (action, endorsees) {
            $.each(endorsees, function (endorsee, v) {
                $.each(v, function (service, v) {
                    $('.' + action + '_' + service + '_' + endorsee).button('reset');
                });
            });
        },

        resetEndorseButton = function (endorsees) {
            resetActionButton('endorse', endorsees);
        };
    return {
        load: load,
        endorse: endorse,
        gatherEndorsementsByRow: gatherEndorsementsByRow,
        updateEndorsementForRowContext: updateEndorsementForRowContext,
        updateEndorsementRows: updateEndorsementRows,
        updateExpireWarning: updateExpireWarning,
        resetActionButton: resetActionButton,
        resetEndorseButton: resetEndorseButton
    };
}());

export { Endorse };
