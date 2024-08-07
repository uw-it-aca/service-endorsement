// javascript to Manage Shared Netids
/* jshint esversion: 6 */

import { Endorse } from "../endorse.js";
import { Revoke } from "../revoke.js";
import { Renew } from "../renew.js";
import { Reasons } from "../reasons.js";
import { Banner } from "../banner.js";
import { Button } from "../button.js";
import { Scroll } from "../scroll.js";
import { Notify } from "../notify.js";

var ManageSharedNetids = (function () {
    var content_id = 'shared',
        location_hash = '#' + content_id,
        table_css,

    _loadContent = function () {
        var content_template = Handlebars.compile($("#shared-netids").html());

        $(location_hash).append(content_template());
        _getSharedUWNetIDs();
    },

    _registerEvents = function () {
        var $panel = $(location_hash);

        $panel.on('click', 'button.endorse_service', function(e) {
            Endorse.endorse('shared_accept_modal_content', $(this).closest('tr'));
        }).on('click', 'button.aggregate_endorse_service', function(e) {
            var $checked_rows = $('tr:not(".visually-hidden") input[id^="aggregate_"]:checked', $panel).closest('tr'),
                $to_endorse = $checked_rows.find('.endorse_service:enabled').closest('tr');

            Endorse.endorse('shared_accept_modal_content', $to_endorse);
        }).on('click', 'button.revoke_service', function(e) {
            Revoke.revoke($(this).closest('tr'));
        }).on('click', 'button.aggregate_revoke_service', function(e) {
            var $checked_rows = $('tr:not(".visually-hidden") input[id^="aggregate_"]:checked', $panel).closest('tr'),
                $to_revoke = $checked_rows.find('.revoke_service:enabled').closest('tr');

            Revoke.revoke($to_revoke);
        }).on('click', 'button.renew_service', function(e) {
            Renew.renew($(this).closest('tr'));
        }).on('click', 'button.aggregate_renew_service', function(e) {
            var $checked_rows = $('tr:not(".visually-hidden") input[id^="aggregate_"]:checked', $panel).closest('tr'),
                $to_renew = $checked_rows.find('.renew_service:enabled').closest('tr');

            Renew.renew($to_renew);
        }).on('click', '#check_all', function(e) {
            $('tr:not(".visually-hidden") input[id^="aggregate_"]', $panel).prop('checked', $(this).prop('checked'));
            _enableSharedEndorsability();
        }).on('endorse:PanelToggleExposed', function (e, $div) {
            $('.aggregate_action', $panel).removeClass('visually-hidden');
            $('input[id^="aggregate_"]', $panel).prop('checked', false);
            _enableSharedEndorsability();
        }).on('endorse:PanelToggleHidden', function (e, $div) {
            $('.aggregate_action', $panel).addClass('visually-hidden');
        }).on('endorse:UWNetIDReasonEdited endorse:UWNetIDChangedReason endorse:UWNetIDApplyAllReasons', function (e) {
            _enableSharedEndorsability();
        }).on('click', 'button#confirm_shared_endorse', function(e) {
            $(this).parents('.modal').modal('hide');
            Button.loading($('button#shared_update'));
            var shared = _getSharedUWNetIDsToEndorse();

            _endorseSharedUWNetIDs(shared);
        }).on('focus', 'div.shared-netids-table', function(e) {
            // console.log("focus shared");
        }).on('endorse:UWNetIDsEndorseSuccess', function (e, data) {
            Endorse.updateEndorsementRows(data.endorsed.endorsed);
            _enableSharedEndorsability();

            // pause for shared endorse modal fade
            if (data.endorsed.endorsed && _validEndorsementResults(data.endorsed.endorsed)) {
                setTimeout(function () {
                    _enableSharedEndorsability();
                    _sharedEndorseSuccessModal(data.endorsed.endorsed);
                }, 500);
            }

            Banner.renderMessages(data.endorsed.messages);
        }).on('endorse:UWNetIDsEndorseError', function (e, endorsees, error) {
            Notify.error('Unable to Endorse at this time: ' + error);
            Endorse.resetEndorseButton(endorsees);
        }).on('endorse:UWNetIDsRevokeSuccess', function (e, data) {
            Endorse.updateEndorsementRows(data.revoked.endorsed);
            _enableSharedEndorsability();
        }).on('endorse:UWNetIDsRevokeError', function (e, revokees, error) {
            Notify.error('Unable to Revoke at this time: ' + error);
            Revoke.resetRevokeButton(revokees);
        }).on('endorse:UWNetIDsRenewSuccess', function (e, data) {
            Endorse.updateEndorsementRows(data.renewed.endorsed);
            _enableSharedEndorsability();
        }).on('endorse:UWNetIDsRenewError', function (e, renewees, error) {
            Notify.error('Unable to Renew at this time: ' + error);
            Renew.resetRenewButton(renewees);
        });

        $(document).on('endorse:UWNetIDRevoking', function (e, $row) {
            _enableSharedEndorsability($row);
        }).on('endorse:UWNetIDsInvalidReasonError', function (e, $row, $td) {
            if ($('input[type="checkbox"]:checked', $row).length > 0) {
                $td.addClass('error');
                $('button#shared_update').prop('disabled', true);
            }
        }).on('endorse:UWNetIDsShared', function (e, shared) {
            _displaySharedUWNetIDs(shared);
        }).on('endorse:UWNetIDsSharedError', function (e, error) {
            $(location_hash + '.content').html($('#shared-failure').html());
        }).on('endorse:DisplayFilterChange', function (e) {
            _enableSharedEndorsability();
        });
    },

    _displaySharedUWNetIDs = function(shared) {
        var $panel = $(location_hash),
            $content = $('.form-group.content', $panel),
            source,
            template,
            context = {
                shared: shared
            };

        if (shared.shared && shared.shared.length > 0) {
            source = $("#shared-netids-content").html();
            template = Handlebars.compile(source);

            $.each(context.shared.shared, function () {
                var endorsements = this.endorsements,
                    svc,
                    endorsement_count = 0;

                if (endorsements) {
                    for (svc in endorsements) {
                        if (endorsements.hasOwnProperty(svc)) {
                            if (endorsements[svc]) {
                                Endorse.updateEndorsementForRowContext(endorsements[svc]);
                            }
                            endorsement_count += 1;
                        }
                    }
                }
            });

            Banner.renderMessages(shared.messages);
        } else {
            source = $("#no-shared-netids-content").html();
            template = Handlebars.compile(source);
        }

        $content.html(template(context));
        _enableSharedEndorsability();
        Endorse.updateExpireWarning();
        Scroll.init('.shared-netids-table');
    },

    _enableSharedEndorsability = function() {
        var $panel = $(location_hash);

        // enable/disable Provision button
        $('.displaying-reasons select', $panel).each(function () {
            var $this = $(this);

            if ($('option:selected', $this).val() !== '') {
                $('button.endorse_service', $this.closest('tr')).prop('disabled', false);
            }
        });

        // fixup checkboxes, aggregate labels
        if ($('.panel-toggle + .form-group.content', $panel).hasClass('visually-hidden') === false) {
            var $checked = $('tr:not(".visually-hidden") input[id^="aggregate_"]:checked', $panel),
                $rows = $checked.closest('tr:not(".visually-hidden")'),
                is_checked = false,
                is_indeterminate = false,
                $check_all = $('input#check_all', $panel),
                n_total, n_renew = 0, n_revoke = 0, n_endorse = 0;

            if ($checked.length > 0) {
                var total = $('tr:not(".visually-hidden") input[id^="aggregate_"]', $panel).length;

                $('.aggregate_action', $panel).removeClass('visually-hidden');

                if ($checked.length < total) {
                    is_indeterminate = true;
                } else {
                    is_checked = true;
                }
            }

            $check_all.prop('indeterminate', is_indeterminate);
            $check_all.prop('checked', is_checked);

            // fixup error labels
            $('.shared-netids-table > table > tbody > tr', $panel).removeClass('error');
            $.each(['endorse', 'renew', 'revoke'], function (i, action) {
                var $agg_button = $('.aggregate_' + action + '_service', $panel),
                    $enabled =  $('.' + action + '_service:enabled', $rows),
                    $disabled =  $('.' + action + '_service:disabled', $rows),
                    check_count = $enabled.length + $disabled.length;

                if (check_count) {
                    $('span', $agg_button).html('(' + check_count + ') ');
                    if ($disabled.length > 0) {
                        $agg_button.prop('disabled', true);
                    } else {
                        $agg_button.prop('disabled', false);
                    }
                } else {
                    $agg_button.prop('disabled', true);
                    $('span', $agg_button).html('');
                }

                $disabled.closest('tr').addClass('error');
            });
        }
    },

    _getSharedUWNetIDsToEndorse = function () {
        var aggregate = {
            'endorse': {},
            'revoke': {},
            'renew': {}
        };

        $('input[id^="aggregate_"]:checked').each(function () {
            var $checkbox = $(this),
                $row = $checkbox.closest('tr'),
                netid = $row.attr('data-netid'),
                service = $row.attr('data-service'),
                service_name = $row.attr('data-service-name'),
                $provision = $('.endorse_service:enabled', $row),
                $revoke = $('.revoke_service:enabled', $row),
                $renew = $('.renew_service:endabled', $row);

            if (netid) {
                if ($provision.length) {
                    var endorse = {
                        name: '',
                        email: '',
                        reason: Reasons.getReason($row),
                    };

                    if (!aggregate.endorse.hasOwnProperty(netid)) {
                        aggregate.endorse[netid] = {
                            state: true
                        };
                    }

                    aggregate.endorse[netid][service] = endorse;
                }

                if ($revoke.length) {
                    if (!aggregate.revoke.hasOwnProperty(netid)) {
                        aggregate.revoke[netid] = {};
                    }

                    aggregate.revoke[netid][service] = {
                        state: false
                    };
                }

                if ($renew.length) {
                    if (!aggregate.renew.hasOwnProperty(netid)) {
                        aggregate.renew[netid] = {};
                    }

                    aggregate.renew[netid][service] = {
                        name: netid
                    };
                }
            }
        });

        return aggregate;
    },

    _getSharedUWNetIDs = function() {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
            $panel = $(location_hash);

        $('.form-group.content', $panel).html($('#shared-loading').html());

        $.ajax({
            url: "/api/v1/shared/",
            dataType: "JSON",
            type: "GET",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                $panel.trigger('endorse:UWNetIDsShared', [results]);
            },
            error: function(xhr, status, error) {
                $panel.trigger('endorse:UWNetIDsSharedError', [error]);
            }
        });
    },

    _sharedEndorseSuccessModal = function (endorsements) {
        var source = $("#shared_provisioned_modal_content").html(),
            template = Handlebars.compile(source),
            $modal = $('#shared_netid_modal'),
            context = {
                unique: [],
                services: {}
            };

        $.each(window.endorsed_services, function(k, v) {
            context.services[k] = {
                'name': v.category_name,
                'service_link': v.service_link,
                'endorsed': []
            };

            $.each(endorsements, function (netid, e) {
                if (context.unique.indexOf(netid) < 0) {
                    context.unique.push(netid);
                }

                if (e.endorsements.hasOwnProperty(k)) {
                    context.services[k].endorsed.push({
                        netid: netid
                    });
                }
            });
        });

        context.netid_count = context.unique.length;

        $.each(context.services, function(k) {
            context.services[k].count = context.services[k].endorsed.length;
        });

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
    },

    _validEndorsementResults = function (endorsed) {
        var is_success = true;

        $.each(endorsed, function (netid, endorsements) {
            $.each(endorsements.endorsements, function (service, state) {
                if (state.hasOwnProperty('error')) {
                    is_success = false;
                    return false;
                }
            });

            if (!is_success) {
                return false;
            }
        });

        return is_success;
    };

    return {
        load: function () {
            _loadContent();
            _registerEvents();
        }
    };
}());

export { ManageSharedNetids };
