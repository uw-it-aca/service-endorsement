// javascript to Manage Shared Netids

var ManageSharedNetids = {
    hash: '#shared',

    load: function () {
        this._loadTab();
        this._registerEvents();
    },

    focus: function () {
        if (window.location.hash === this.hash) {
            $('a[href="' + this.hash + '"]').tab('show');
        }
    },

    _loadTab: function () {
        var tab_link = $("#shared-netids-tab-link").html(),
            tab_content = $("#shared-netids-tab-content").html();
        
        $('.nav-tabs').append(tab_link);
        $('.tab-content').append(tab_content);
    },

    _registerEvents: function () {
        $(ManageSharedNetids.hash).on('click', 'button.confirm_revoke', function(e) {
            Revoke.revoke($(this), '#shared_revoke_modal_content',
                          'endorse:SharedUWNetIDsRevokeStatus');
        });

        $(document).on('shown.bs.tab', 'a[href="#shared"]', function (e) {
            // load once
            if ($('#shared table').length === 0) {
                ManageSharedNetids._getSharedUWNetIDs();
            }
        }).on('endorse:UWNetIDRevoking', function (e, validated) {
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:UWNetIDReasonEdited', function (e, validated) {
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:UWNetIDChangedReason', function (e) {
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:UWNetIDApplyAllReasons', function (e) {
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:SharedUWNetIDsRevokeStatus', function (e, data) {
            ManageSharedNetids._updateSharedEndorsementStatus(data.revoked);
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:SharedUWNetIDsEndorseStatus', function (e, endorsed) {
            ManageSharedNetids._updateSharedEndorsementStatus(endorsed);
            ManageSharedNetids._enableSharedEndorsability();
        }).on('endorse:SharedUWNetIDsEndorseSuccess', function (e, netid, service, service_name) {
            // pause for shared endorse modal fade
            $('button#shared_update').button('reset');
            setTimeout(function () {
                ManageSharedNetids._enableSharedEndorsability();
                ManageSharedNetids._sharedEndorseSuccessModal(netid, service, service_name);
            }, 500);
        }).on('endorse:SharedUWNetIDsEndorseStatusError', function (e, netid, service, error) {
            $('button#shared_update').button('reset');
        }).on('endorse:UWNetIDsShared', function (e, shared) {
            ManageSharedNetids._displaySharedUWNetIDs(shared);
        }).on('click', 'button#confirm_shared_endorse', function(e) {
            $(this).parents('.modal').modal('hide');
            $('button#shared_update').button('loading');
            ManageSharedNetids._endorseSharedUWNetIDs(ManageSharedNetids._getSharedUWNetIDsToEndorse());
        }).on('click', 'button#shared_update', function(e) {
            ManageSharedNetids._sharedEndorseAcceptModal(ManageSharedNetids._getSharedUWNetIDsToEndorse());
        }).on('change', 'input[id^="endorse_"]', function (e) {
            ManageSharedNetids._enableSharedEndorsability();
        }).on('change', 'input[id^="shared_accept_responsibility"]', function(e) {
            var boxes = $('input[id^="shared_accept_responsibility"]').length,
                checked = $('input[id^="shared_accept_responsibility"]:checked').length;

            if (boxes === checked) {
                $('button#confirm_shared_endorse').removeAttr('disabled');
            } else {
                $('button#confirm_shared_endorse').attr('disabled', 'disabled');
            }
        }).on('show.bs.modal', '#shared_netid_modal' ,function (event) {
            var _modal = $(this);

            _modal.find('input#shared_accept_responsibility').attr('checked', false);
            _modal.find('button#confirm_shared_endorse').attr('disabled', 'disabled');
        });
    },

    _displaySharedUWNetIDs: function(shared) {
        var source = $("#shared-netids").html(),
            template = Handlebars.compile(source),
            context = {
                has_shared: shared.shared && shared.shared.length > 0,
                shared: shared
            };

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

        $('div.tab-pane#shared').html(template(context));
        ManageSharedNetids._enableSharedEndorsability();
    },

    _enableSharedEndorsability: function() {
        var $button = $('button#shared_update'),
            netids;

        $('td.error').removeClass('error');
        netids = ManageSharedNetids._getSharedUWNetIDsToEndorse();
        if (Object.keys(netids).length > 0 &&
            $('td.error').length === 0) {
            $button.removeAttr('disabled');
        } else {
            $button.attr('disabled', 'disabled');
        }
    },

    _getSharedUWNetIDsToEndorse: function () {
        var endorsees = {};

        $.each(['o365', 'google'], function () {
            var service_id = this;

            $('input[id^="endorse_' + service_id + '_"]:checked').each(function () {
                var $row = $(this).closest('tr'),
                    netid = this.value;

                if (!endorsees.hasOwnProperty(netid)) {
                    endorsees[netid] = {
                        name: '',
                        email: '',
                        reason: Reasons.getReason($row),
                        store: true
                    };
                }

                endorsees[netid][service_id] = true;
            });
        });

        return endorsees;
    },

    _getSharedUWNetIDs: function() {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $('#shared').html($('#shared-loading').html());

        $.ajax({
            url: "/api/v1/shared/",
            dataType: "JSON",
            type: "GET",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                $(document).trigger('endorse:UWNetIDsShared', [results]);
            },
            error: function(xhr, status, error) {
                $('#shared').html($('#shared-failure').html());
            }
        });
    },

    _endorseSharedUWNetIDs: function(to_endorse) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $.ajax({
            url: "/api/v1/endorse/",
            dataType: "JSON",
            data: JSON.stringify(to_endorse),
            type: "POST",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                $(document).trigger('endorse:SharedUWNetIDsEndorseStatus', [results]);
            },
            error: function(xhr, status, error) {
                $(document).trigger('endorse:SharedUWNetIDsEndorseStatusError', [netid, service, error]);
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
                    $('button.shared_update').button('reset');
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
            $(document).trigger('endorse:SharedUWNetIDsEndorseSuccess', [endorsed]);
        }
    },

    _sharedEndorseAcceptModal: function (endorsements) {
        var source = $("#shared_accept_modal_content").html(),
            template = Handlebars.compile(source),
            $modal = $('#shared_netid_modal'),
            endorse_o365 = [],
            endorse_google = [],
            context = {
                endorse_o365: [],
                endorse_google: [],
                endorse_netid_count: 0,
                endorse_o365_netid_count: 0,
                endorse_google_netid_count: 0
            },
            netid;

        for (netid in endorsements) {
            if (endorsements.hasOwnProperty(netid)) {
                if (endorsements[netid].hasOwnProperty('o365')) {
                    context.endorse_o365.push(netid);
                }

                if (endorsements[netid].hasOwnProperty('google')) {
                    context.endorse_google.push(netid);
                }
            }
        }

        context.endorse_o365_netid_count = context.endorse_o365.length;
        context.endorse_google_netid_count = context.endorse_google.length;
        context.endorse_netid_count = context.endorse_google_netid_count + context.endorse_o365_netid_count;

        $.data($modal[0], 'modal-body-context', context);

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
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
