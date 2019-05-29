// javascript to Manage Provisioned Services

var ManageProvisionedServices = {
    content_id: 'provisioned',
    location_hash: '#provisioned',

    load: function () {
        this._loadContent();
        this._registerEvents();
    },

    _loadContent: function () {
        ManageProvisionedServices._getEndorsedUWNetIDs();
    },

    _registerEvents: function () {
        $panel = $('#' + ManageProvisionedServices.content_id);

        // delegated events within our content
        $panel.on('click', 'button.endorse_service', function(e) {
            Endorse.endorse('endorse_accept_modal_content', $(this).closest('tr'));
        }).on('click', 'button.revoke_service', function(e) {
            Revoke.revoke('revoke_modal_content', $(this).closest('tr'));
        }).on('click', 'button.renew_service', function(e) {
            Renew.renew('renew_modal_content', $(this).closest('tr'));
        }).on('click', '#export_csv', function (e) {
            ManageProvisionedServices._exportProvisionedToCSV();
        }).on('endorse:UWNetIDsEndorsed', function (e, endorsed) {
            $('button#confirm_endorsements').button('reset');
            ManageProvisionedServices._displayEndorsedUWNetIDs(endorsed);
            window.endorsed = endorsed;
        }).on('endorse:UWNetIDsEndorsedError', function (e, error) {
            $('#' + ManageProvisionedServices.content_id).html($('#endorsed-failure').html());
        }).on('endorse:UWNetIDReasonEdited endorse:UWNetIDChangedReason endorse:UWNetIDApplyAllReasons', function (e, $row) {
            $('button.endorse_service', $row).removeAttr('disabled');
        }).on('endorse:PanelToggleExposed', function (e, $div) {
            $('#netid_list', $div).focus();
            ManageProvisionedServices._enableCheckEligibility();
        }).on('endorse:PanelToggleHidden', function (e, $div) {
            $('#uwnetids-input', $div).removeClass('visually-hidden');
            $('#uwnetids-validated', $div).addClass('visually-hidden');
        }).on('input change', '#netid_list', function () {
            ManageProvisionedServices._enableCheckEligibility();
        }).on('click', 'button#validate', function(e) {
            $(this).button('loading');
            ManageProvisionedServices._validateUWNetids(ManageProvisionedServices._getNetidList());
        }).on('click', 'button.button_url', function(e) {
            location.href = $(this).attr('data-url');
        }).on('click', 'button#netid_input', function(e) {
            $('#uwnetids-validated', $panel).addClass('visually-hidden');
            $('#uwnetids-input', $panel).removeClass('visually-hidden').focus();
        }).on('endorse:UWNetIDsValidated', function (e, validated) {
            $('button#validate').button('reset');
            ManageProvisionedServices._displayValidationResult(validated);
        }).on('endorse:UWNetIDsValidatedError', function (e, error) {
            $('button#validate').button('reset');
            Notify.error('Validation error: ' + error);
        }).on('endorse:UWNetIDsEndorseSuccess', function (e, data) {
            Endorse.updateEndorsementRows(data.endorsed.endorsed);
        }).on('endorse:UWNetIDsRenewSuccess', function (e, data) {
            Endorse.updateEndorsementRows(data.renewed.endorsed);
        }).on('endorse:UWNetIDsEndorseError', function (e, error) {
            Notify.error('Unable to Endorse at this time: ' + error);
        }).on('endorse:UWNetIDsRevokeSuccess', function (e, data) {
            Endorse.updateEndorsementRows(data.revoked.endorsed);
        }).on('endorse:UWNetIDsRevokeError', function (e, error) {
            Notify.error('Unable to Revoke at this time: ' + error);
        });
    },

    _getNetidList: function () {
        var netid_list = $('#netid_list').val();

        return (netid_list) ? ManageProvisionedServices._unique(
            netid_list.toLowerCase()
                .replace(/\n/g, ' ')
                .replace(/([a-z0-9]+)(@(uw|washington|u\.washington)\.edu)?/g, '$1')
                .split(/[ ,]+/))
            : [];
    },

    _unique: function(array) {
        return $.grep(array, function(el, i) {
            return el.length > 0 && i === $.inArray(el, array);
        });
    },

    _getEndorsedUWNetIDs: function() {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
            $content = $('#' + ManageProvisionedServices.content_id);

        var source = $("#endorsed-loading").html(),
            template = Handlebars.compile(source),
            $panel = $('#' + ManageProvisionedServices.content_id);

        $content.html(template());

        $.ajax({
            url: "/api/v1/endorsed/",
            dataType: "JSON",
            type: "GET",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                $content.trigger('endorse:UWNetIDsEndorsed', [results]);
            },
            error: function(xhr, status, error) {
                $content.trigger('endorse:UWNetIDsEndorsedError', [error]);
            }
        });
    },

    _enableCheckEligibility: function() {
        var $panel = $('#' + ManageProvisionedServices.content_id),
            netids = ManageProvisionedServices._getNetidList();

        if (netids.length > 0) {
            $('#validate', $panel).removeAttr('disabled');
        } else {
            $('#validate', $panel).attr('disabled', 'disabled');
        }
    },

    _displayValidationResult: function(validated) {
        var $panel = $('#' + ManageProvisionedServices.content_id),
            source = $("#validated_content").html(),
            template = Handlebars.compile(source),
            row_source = $('#endorsee-row').html(),
            row_template = Handlebars.compile(row_source);
            context = {
                netids: {},
                netid_count: 0,
                netids_present: {},
                netids_present_count: 0,
                netid_errors: {},
                netid_error_count: 0
            };

        $.each(validated.validated, function () {
            var netid = this.netid,
                name = this.name,
                email = this.email,
                present = ($('.endorsed-netids-table tr[data-netid="' + netid + '"]', $panel).length > 0),
                $table = $('.endorsed-netids-table table', $panel),
                $row;

            if (present) {
                context.netids_present[netid] = this;
                context.netids_present_count += 1;
            } else if (this.error === undefined) {
                context.netids[netid] = this;
                context.netid_count += 1;

                // insert valid netid into endorsed list
                $('tbody tr', $table).each(function () {
                    if (netid < $(this).attr('data-netid')) {
                        $row = $(this);
                        return false;
                    }
                });

                $.each(this.endorsements, function (svc, endorsement) {
                    var row_html = row_template({
                        netid: netid,
                        name: name,
                        email: email,
                        service: svc,
                        endorsement: endorsement
                    });

                    Endorse.updateEndorsementForRowContext(endorsement);

                    if ($row) {
                        $row.before(row_html);
                    } else {
                        $('tbody').append(row_html);
                    }
                });
            } else {
                context.netid_errors[this.netid] = this;
                context.netid_error_count += 1;
            }
        });

        $('#uwnetids-validated', $panel)
            .html(template(context))
            .removeClass('visually-hidden');
        $('#uwnetids-input', $panel).addClass('visually-hidden');
    },

    _displayEndorsedUWNetIDs: function(endorsed) {
        var source = $("#endorsed-netids").html(),
            template = Handlebars.compile(source),
            context = {
                can_revoke: true,
                has_endorsed: (endorsed && Object.keys(endorsed.endorsed).length > 0),
                endorsed: endorsed
            },
            $panel = $('#' + ManageProvisionedServices.content_id);

        // figure out renewal dates and expirations
        $.each(endorsed ? endorsed.endorsed : [], function (netid, data) {
            $.each(data.endorsements, function (service, endorsement) {
                Endorse.updateEndorsementForRowContext(endorsement);
            });
        });

        $panel.html(template(context));
        $panel.find('ul').each(function () {
            var pending = $('.current-endorsee', this);

            if (pending.length) {
                pending.appendTo($(this));
            }
        });
    },

    _validateUWNetids: function(netids) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
            $panel = $('#' + ManageProvisionedServices.content_id);

        $.ajax({
            url: "/api/v1/validate/",
            dataType: "JSON",
            data: JSON.stringify(netids),
            type: "POST",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                window.endorsement = { validation: results };
                $panel.trigger('endorse:UWNetIDsValidated', [results]);
            },
            error: function(xhr, status, error) {
                $panel.trigger('endorse:UWNetIDsValidatedError', [error]);
            }
        });
    },

    _exportProvisionedToCSV: function() {
        var $table = $('#provisioned table'),
            endorsed = window.endorsed.endorsed,
            colDelim = ',',
            rowDelim = '\r\n',
            data = [[]],
            fields = [],
            csv,
            downlink;

        // csv header fields
        $('thead tr th', $table).each(function (i) {
            var label = $(this).attr('data-csv-label');

            if (label !== undefined) {
                data[0].push(label);
                fields.push(i);
            }
        });

        // collect csv data from table
        $('tr', $table).each(function () {
            var $cols = $(this).find('td'),
                msg;

            if ($cols.length) {
                var row = [];

                $.each(fields, function(i, n) {
                    var $col = $($cols.get(n)),
                        provisioned = $col.attr('data-csv-provisioned'),
                        reason = $col.attr('data-csv-reason'),
                        endorsement,
                        context;

                    if (provisioned) {
                        msg = '';
                        context = provisioned.split('-');
                        endorsement = endorsed[context[1]] && endorsed[context[1]][context[0]];

                        if (endorsement) {
                            if (endorsement.datetime_endorsed) {
                                msg += 'provisioned ' +  utc2local(endorsement.datetime_endorsed);
                            } else {
                                msg += 'pending acceptance';
                            }

                            if (endorsement.hasOwnProperty('endorsers') && endorsement.endorsers.length > 1) {
                                msg += " (also provisioned by ";

                                $.each(endorsement.endorsers, function (i) {
                                    if (this.netid != endorsement.endorser.netid) {
                                        if (i > 0) {
                                            msg += ', ';
                                        }

                                        msg += this.netid;
                                    }
                                });

                                msg += ')';
                            }

                        } else {
                            msg += 'not provisioned';
                        }

                        row.push(msg);
                    } else if (reason) {
                        msg = '';
                        context = reason.split('-');
                        endorsement = endorsed[context[1]] && endorsed[context[1]][context[0]];
                        if (endorsement) {
                            msg += endorsement.reason;
                        }

                        row.push(msg);
                    } else {
                        row.push($col.html());
                    }
                });

                data.push(row);
            }
        });

        // generate csv, escaping delims and quotes
        csv = data.map(function(row) {
            return row.map(function(col) {
                var escaped = col.replace(/"/g, '""');

                if (escaped.indexOf('"') >= 0 || escaped.indexOf(colDelim) >= 0) {
                    escaped = '"' + escaped + '"';
                }

                return escaped;
            }).join(colDelim);
        }).join(rowDelim);

        // download
        downlink = document.createElement('a');
        downlink.href = 'data:application/csv;charset=utf-8,' + encodeURIComponent(csv);
        downlink.target = '_blank';
        downlink.download = 'provisioned.csv';
        downlink.click();
    }
};
