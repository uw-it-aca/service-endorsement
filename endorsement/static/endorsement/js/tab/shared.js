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
        }).on('click', 'button.confirm_revoke', function(e) {
            Revoke.revoke($(this), '#shared_revoke_modal_content',
                          'endorse:SharedUWNetIDsRevokeStatus');
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
        }).on('endorse:SharedUWNetIDsRevokeStatus', function (e, data) {
            ManageSharedNetids._updateSharedEndorsementStatus(data.revoked);
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:UWNetIDsShared', function (e, shared) {
            ManageSharedNetids._displaySharedUWNetIDs(shared);
        }).on('endorse:UWNetIDsSharedError', function (e, error) {
            $('#' + ManageSharedNetids.content_id + '.content').html($('#shared-failure').html());
        }).on('endorse:UWNetIDsEndorseSuccess', function (e, data) {
            var row_source = $('#endorsee-row').html(),
                row_template = Handlebars.compile(row_source);

            $.each(data.endorsed.endorsed, function (netid, endorsements) {
                var name = endorsements.name,
                    email = endorsements.email;

                $.each(endorsements.endorsements, function (service, endorsement) {
                    var $row = $('tr[data-netid="' + netid + '"][data-service="' + service + '"]');

                    if ($row.length) {
                        $row.replaceWith(row_template({
                            netid: netid,
                            email: email,
                            name: name,
                            service: service,
                            endorsement: endorsement
                        }));
                    }
                });
            });
            // pause for shared endorse modal fade
/*
            $('button#shared_update').button('reset');
            setTimeout(function () {
                ManageSharedNetids._enableSharedEndorsability();
                ManageSharedNetids._sharedEndorseSuccessModal(netid, service, service_name);
            }, 500);
*/
        }).on('endorse:UWNetIDsEndorseError', function (e, error) {
            console.log('error: ' + error);
        }).on('endorse:UWNetIDsRevokeStatus', function (e, data) {
            var row_source = $('#endorsee-row').html(),
                row_template = Handlebars.compile(row_source);

            $.each(data.revokees, function (netid, endorsements) {
                $.each(endorsements, function (endorsement, state) {
                    var $row = $('tr[data-netid="' + netid + '"][data-service="' + endorsement + '"]');

                    if ($row.length) {
                        $row.replaceWith(row_template({
                            netid: netid,
                            name: $row.attr('data-netid-name'),
                            email: $row.attr('data-netid-initial-email'),
                            service: endorsement,
                            endorsement: {
                                category_name: $row.attr('data-service-name'),
                                active: false,
                                endorsers: []
                            }
                        }));
                    }
                });
            });
        }).on('endorse:UWNetIDsRevokeStatusError', function (e, error) {
            console.log('error: ' + error);
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
                                if (endorsements[svc].hasOwnProperty('datetime_endorsed')) {
                                    endorsements[svc].date_endorsed = utc2localdate(endorsements[svc].datetime_endorsed);
                                }
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

            // fixup labels
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
                        store: true
                    };

                    if (!aggregate.endorse.hasOwnProperty(netid)) {
                        aggregate.endorse[netid] = {};
                    }

                    aggregate.endorse[netid][service] = endorse;
                }

                if ($revoke.length) {
                    aggregate.revoke[netid][service] = {
                        name: netid,
                        store: true
                    };
                }

                if ($renew.length) {
                    aggregate.renew[netid][service] = {
                        name: netid,
                        store: false
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

    _updateSharedEndorsementStatus: function(endorsed) {
        var endorsers_template = Handlebars.compile(
            $("#endorsers_partial").html()),
            reason_template = Handlebars.compile(
                $("#reasons_partial").html()),
            action_template = Handlebars.compile(
                $("#endorse_button_partial").html()),
            success = false,
            netid;

        $.each(endorsed.endorsed, function(netid, endorsements) {
            $.each(['o365', 'google'], function () {
                var service_id = this,
                    endorsement,
                    $row;

                if (endorsements.hasOwnProperty('error')) {
                    Notify.error('Error provisioning shared netid "' + netid + '"');
                    $('button#shared_update').button('reset');
                    return;
                }

                if (endorsements.hasOwnProperty(service_id)) {
                    endorsement = endorsements[service_id];
                    $row = $('#endorsers-' + service_id + '-' + netid).closest('tr');

                    if (endorsement.hasOwnProperty('datetime_endorsed')) {
                        endorsement.date_endorsed = utc2localdate(endorsement.datetime_endorsed);
                    }
                    
                    $('#endorsers-' + service_id + '-' + netid).html(endorsers_template({
                        netid: netid,
                        svc: service_id,
                        endorsement: endorsement.endorsed ? endorsement : null
                    }));

                    $('#reason-' + service_id + '-' + netid).html(reason_template({
                        endorsements: endorsement.endorsed ? endorsements : null
                    }));

                    if (endorsement.endorsed || $('button.confirm_revoke', $row).length === 0) {
                        $('#reason-' + netid).html(reason_template({
                            endorsements: endorsement.endorsed ? endorsements : null
                        }));
                    }

                    if (!success && endorsement.endorsed) {
                        success = true;
                    }
                }
            });
        });

        if (success) {
            $(document).trigger('endorse:UWNetIDsEndorseSuccess', [endorsed]);
        }
    },

    _sharedEndorseSuccessModal: function (netid, service, service_name) {
        var source = $("#shared_provisioned_modal_content").html(),
            template = Handlebars.compile(source),
            $modal = $('#shared_netid_modal'),
            context = $.data($modal[0], 'modal-body-context');

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
    }
};
