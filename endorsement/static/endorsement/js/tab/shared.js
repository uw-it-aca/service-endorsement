// javascript to Manage Shared Netids

var ManageSharedNetids = {
    content_id: 'shared',
    location_hash: '#shared',

    load: function () {
        this._loadContent();
        this._registerEvents();
    },

    _loadContent: function () {
        var content_template = Handlebars.compile($("#shared-netids").html())

        $('#' + ManageSharedNetids.content_id).append(content_template());
        ManageSharedNetids._getSharedUWNetIDs();
    },

    _registerEvents: function () {
        var $panel = $('#' + ManageSharedNetids.content_id);

        $panel.on('click', 'button.endorse_service', function(e) {
            Endorse.endorse('shared_accept_modal_content', $(this).closest('tr'))
        }).on('click', 'button.aggregate_endorse_service', function(e) {
            Endorse.endorse('shared_accept_modal_content',
                            $('input[id^="aggregate_"]:checked').closest('tr'));
        }).on('click', 'button.revoke_service', function(e) {
            Revoke.revoke('shared_revoke_modal_content', $(this).closest('tr'));
        }).on('click', 'button.aggregate_revoke_service', function(e) {
            Revoke.revoke('shared_revoke_modal_content',
                          $('input[id^="aggregate_"]:checked').closest('tr'));
        }).on('click', 'button.renew_service', function(e) {
            Renew.renew('shared_renew_modal_content', $(this).closest('tr'));
        }).on('click', 'button.aggregate_renew_service', function(e) {
            Renew.renew('shared_renew_modal_content',
                        $('input[id^="aggregate_"]:checked').closest('tr'));
        }).on('click', '#check_all', function(e) {
            $('input[id^="aggregate_"]', $panel).prop('checked', $(this).prop('checked'));
            ManageSharedNetids._enableSharedEndorsability();
        }).on('change', 'input[id^="aggregate_"]', function(e) {
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:PanelToggleExposed', function (e, $div) {
            $('.aggregate_action', $panel).removeClass('visually-hidden');
            $('input[id^="aggregate_"]', $panel).prop('checked', false);
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:PanelToggleHidden', function (e, $div) {
            $('.aggregate_action', $panel).addClass('visually-hidden');
        }).on('endorse:UWNetIDReasonEdited endorse:UWNetIDChangedReason endorse:UWNetIDApplyAllReasons', function (e) {
            ManageSharedNetids._enableSharedEndorsability();
        }).on('click', 'button#confirm_shared_endorse', function(e) {
            $(this).parents('.modal').modal('hide');
            $('button#shared_update').button('loading');
            var shared = ManageSharedNetids._getSharedUWNetIDsToEndorse();

            ManageSharedNetids._endorseSharedUWNetIDs(shared);
        }).on('endorse:UWNetIDsEndorseSuccess', function (e, data) {
            Endorse.updateEndorsementRows(data.endorsed.endorsed);
            ManageSharedNetids._enableSharedEndorsability();

            // pause for shared endorse modal fade
            if (data.endorsed.endorsed) {
                setTimeout(function () {
                    ManageSharedNetids._enableSharedEndorsability();
                    ManageSharedNetids._sharedEndorseSuccessModal(data.endorsed.endorsed);
                }, 500);
            }
        }).on('endorse:UWNetIDsEndorseError', function (e, error) {
            console.log('error: ' + error);
        }).on('endorse:UWNetIDsRevokeSuccess', function (e, data) {
            Endorse.updateEndorsementRows(data.revoked.endorsed);
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:UWNetIDsRevokeError', function (e, error) {
            console.log('error: ' + error);
        }).on('endorse:UWNetIDsRenewSuccess', function (e, data) {
            Endorse.updateEndorsementRows(data.renewed.endorsed);
            ManageSharedNetids._enableSharedEndorsability();
        });

        $(document).on('endorse:UWNetIDRevoking', function (e, $row) {
            ManageSharedNetids._enableSharedEndorsability($row);
        }).on('endorse:UWNetIDsInvalidReasonError', function (e, $row, $td) {
            if ($('input[type="checkbox"]:checked', $row).length > 0) {
                $td.addClass('error');
                $('button#shared_update').attr('disabled', 'disabled');
            }
        }).on('change', 'input[id^="endorse_"]', function (e) {
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:UWNetIDsShared', function (e, shared) {
            ManageSharedNetids._displaySharedUWNetIDs(shared);
        }).on('endorse:UWNetIDsSharedError', function (e, error) {
            $('#' + ManageSharedNetids.content_id + '.content').html($('#shared-failure').html());
        });
    },

    _displaySharedUWNetIDs: function(shared) {
        var $panel = $('#' + ManageSharedNetids.content_id),
            $content = $('.content', $panel),
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
                    svc;

                if (endorsements) {
                    for (svc in endorsements) {
                        if (endorsements.hasOwnProperty(svc)) {
                            if (endorsements[svc]) {
                                Endorse.updateEndorsementForRowContext(endorsements[svc]);
                            }
                        }
                    }
                }
            });
        } else {
            source = $("#no-shared-netids-content").html();
            template = Handlebars.compile(source);
        }

        $content.html(template(context));
        ManageSharedNetids._enableSharedEndorsability();
    },

    _enableSharedEndorsability: function() {
        var $panel = $('#' + ManageSharedNetids.content_id);

        // enable/disable Provision button
        $('.displaying-reasons select', $panel).each(function () {
            var $this = $(this);

            if ($('option:selected', $this).val() != '') {
                $('button.endorse_service', $this.closest('tr')).removeAttr('disabled');
            }
        });

        // fixup checkboxes, aggregate labels
        if ($('.panel-toggle + div.content', $panel).hasClass('visually-hidden') === false) {
            var $checked = $('tr:not(".visually-hidden") input[id^="aggregate_"]:checked', $panel),
                $rows = $checked.closest('tr'),
                is_checked = false,
                is_indeterminate = false,
                $check_all = $('input#check_all', $panel),
                n_total, n_renew = 0, n_revoke = 0, n_endorse = 0;


            $('.aggregate_action', $panel).removeClass('visually-hidden');

            if ($checked.length > 0) {
                total = $('tr:not(".visually-hidden") input[id^="aggregate_"]', $panel).length;

                if ($checked.length < total) {
                    is_indeterminate = true;
                } else {
                    is_checked = true;
                }
            }

            $check_all.prop('indeterminate', is_indeterminate);
            $check_all.prop('checked', is_checked);

            // fixup error labels
            $('.endorsed-netids-table > table > tbody > tr', $panel).removeClass('error');
            $.each(['endorse', 'renew', 'revoke'], function (i, action) {
                var $agg_button = $('.aggregate_' + action + '_service', $panel),
                    $enabled =  $('.' + action + '_service:enabled', $rows),
                    $disabled =  $('.' + action + '_service:disabled', $rows),
                    check_count = $enabled.length + $disabled.length;

                if (check_count) {
                    $('span', $agg_button).html('(' + check_count + ') ');
                    if ($disabled.length > 0) {
                        $agg_button.attr('disabled', 'disabled');
                    } else {
                        $agg_button.removeAttr('disabled');
                    }
                } else {
                    $agg_button.attr('disabled', 'disabled');
                    $('span', $agg_button).html('');
                }

                $disabled.closest('tr').addClass('error');
            })
        }
    },

    _getSharedUWNetIDsToEndorse: function () {
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

    _getSharedUWNetIDs: function() {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
            $panel = $('#' + ManageSharedNetids.content_id);

        $('.content', $panel).html($('#shared-loading').html());

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

    _sharedEndorseSuccessModal: function (endorsements) {
        var source = $("#shared_provisioned_modal_content").html(),
            template = Handlebars.compile(source),
            $modal = $('#shared_netid_modal'),
            context = {
                endorse_o365: [],
                endorse_google: [],
                endorse_netid_count: 0,
                endorse_o365_netid_count: 0,
                endorse_google_netid_count: 0
            };

        $.each(endorsements, function (netid, services) {
            if (services.endorsements.hasOwnProperty('o365')) {
                context.endorse_o365.push({
                    netid: netid
                });
            }

            if (services.endorsements.hasOwnProperty('google')) {
                context.endorse_google.push({
                    netid: netid
                });
            }
        });

        context.endorse_o365_netid_count = context.endorse_o365.length;
        context.endorse_google_netid_count = context.endorse_google.length;
        context.endorse_netid_count = context.endorse_google_netid_count + context.endorse_o365_netid_count;

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
    }
};
