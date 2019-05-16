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
        }).on('endorse:UWNetIDsRevokeSuccess', function (e, data) {
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
                            type: $row.attr('data-netid-type'),
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
        }).on('endorse:UWNetIDsRevokeError', function (e, error) {
            console.log('error: ' + error);
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
        }).on('endorse:UWNetIDsEndorseSuccess', function (e, data) {
            var row_source = $('#endorsee-row').html(),
                row_template = Handlebars.compile(row_source);

            $.each(data.endorsed.endorsed, function (netid, endorsements) {
                var name = endorsements.name,
                    email = endorsements.email;

                if (endorsements.error) {
                    Notify.error('Error provisioning netid "' + netid + '"');
                    $('button.endorse_service', $('tr[data-netid="' + netid + '"]')).button('reset');
                } else {
                    $.each(endorsements.endorsements, function (service, endorsement) {
                        var $row = $('tr[data-netid="' + netid + '"][data-service="' + service + '"]');

                        ManageSharedNetids._fixEndorsementForContext(endorsement);
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
                }
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
                                ManageSharedNetids._fixEndorsementForContext(endorsements[svc]);
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

    _fixEndorsementForContext: function (endorsement) {
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

            endorsement.expires = expires.format('M/D/YYYY')
            endorsement.expires_relative = expires.fromNow()
                    
            if (now.isBetween(expiring, expires)) {
                endorsement.expiring = endorsement.expires;
            }

            if (now.isAfter(expires)) {
                endorsement.expired = endorsement.expires;
            }
        }
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

    _sharedEndorseSuccessModal: function (netid, service, service_name) {
        var source = $("#shared_provisioned_modal_content").html(),
            template = Handlebars.compile(source),
            $modal = $('#shared_netid_modal'),
            context = $.data($modal[0], 'modal-body-context');

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
    }
};
