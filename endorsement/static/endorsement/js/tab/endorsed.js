// javascript to Manage Provisioned Services
/* jshint esversion: 6 */

import { Endorse } from "../endorse.js";
import { Revoke } from "../revoke.js";
import { Renew } from "../renew.js";
import { Reasons } from "../reasons.js";
import { Notify } from "../notify.js";

var ManageProvisionedServices = (function () {
    var content_id = 'provisioned',
        location_hash = '#' + content_id,
        table_css = null,

    _getEndorsedUWNetIDs = function() {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
            $content = $(location_hash);

        var source = $("#endorsed-loading").html(),
            template = Handlebars.compile(source),
            $panel = $(location_hash);

        $content.html(template());

        $.ajax({
            url: "/api/v1/endorsed/",
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

    _displayEndorsedUWNetIDs = function(endorsed) {
        var source = $("#endorsed-netids").html(),
            template = Handlebars.compile(source),
            context = {
                can_revoke: true,
                has_endorsed: (endorsed && Object.keys(endorsed.endorsed).length > 0),
                endorsed: endorsed
            },
            $panel = $(location_hash),
            endorsement_count;

        // figure out renewal dates and expirations
        $.each(endorsed ? endorsed.endorsed : [], function (netid, data) {
            $.each(data.endorsements, function (service, endorsement) {
                Endorse.updateEndorsementForRowContext(endorsement);
            });

            endorsement_count = Object.keys(data.endorsements).length;
        });

        $panel.html(template(context));
        $panel.find('ul').each(function () {
            var pending = $('.current-endorsee', this);

            if (pending.length) {
                pending.appendTo($(this));
            }
        });
    },

    _exportProvisionedToCSV = function() {
        var $table = $('.csv_table'),
            colDelim = ',',
            rowDelim = '\r\n',
            data = [],
            fields = [],
            csv,
            downlink;

        // csv header fields
        $('thead tr th[data-csv-label]', $table).each(function (i) {
            var label = $(this).attr('data-csv-label');

            if (label !== undefined) {
                fields.push(label);
            }
        });

        data.push(fields);

        // collect csv data from table
        $('tr', $table).each(function () {
            var $tr = $(this),
                row = [],
                msg;

            $.each(fields, function(i, n) {
                var $td = $('td[data-csv-' + n + ']', $tr);

                if ($td.length === 0) {
                    if (row.length) {
                        row.push('');
                    } else {
                        return false;
                    }
                }

                if (n === 'reason') {
                    row.push(Reasons.getReason($td));
                } else if (n === 'status') {
                    row.push($('> span', $td).html());
                } else {
                    row.push($td.attr('data-csv-' + n));
                }
            });

            if (row.length) {
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
    },

    _registerEvents = function () {
        var $panel = $(location_hash);

        // delegated events within our content
        $panel.on('click', 'button.endorse_service', function(e) {
            Endorse.endorse('endorse_accept_modal_content', $(this).closest('tr'));
        }).on('click', 'button.revoke_service', function(e) {
            Revoke.revoke($(this).closest('tr'));
        }).on('click', 'button.renew_service', function(e) {
            Renew.renew($(this).closest('tr'));
        }).on('click', '#export_csv', function (e) {
            _exportProvisionedToCSV();
        }).on('endorse:UWNetIDsEndorsed', function (e, endorsed) {
            $('button#confirm_endorsements').button('reset');
            Endorse.updateExpireWarning();
            _displayEndorsedUWNetIDs(endorsed);
        }).on('endorse:UWNetIDsEndorsedError', function (e, error) {
            $(location_hash).html($('#endorsed-failure').html());
        }).on('endorse:UWNetIDReasonEdited endorse:UWNetIDChangedReason endorse:UWNetIDApplyAllReasons', function (e, $row) {
            $('button.endorse_service', $row).removeAttr('disabled');
        }).on('endorse:PanelToggleExposed', function (e, $div) {
            $('#netid_list', $div).focus();
            _enableCheckEligibility();
        }).on('endorse:PanelToggleHidden', function (e, $div) {
            $('#uwnetids-input', $div).removeClass('visually-hidden');
            $('#uwnetids-validated', $div).addClass('visually-hidden');
        }).on('input change', '#netid_list', function () {
            _enableCheckEligibility();
        }).on('click', 'button#validate', function(e) {
            $(this).button('loading');
            _validateUWNetids(_getNetidList());
        }).on('click', 'button.button_url', function(e) {
            location.href = $(this).attr('data-url');
        }).on('click', 'button#netid_input', function(e) {
            $('#uwnetids-validated', $panel).addClass('visually-hidden');
            $('#uwnetids-input', $panel).removeClass('visually-hidden').focus();
        }).on('endorse:UWNetIDsValidated', function (e, validated) {
            $('button#validate').button('reset');
            _displayValidationResult(validated);
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

    _getNetidList = function () {
        var netid_list = $('#netid_list').val();

        return (netid_list) ? _unique(
            netid_list.toLowerCase()
                .replace(/\n/g, ' ')
                .replace(/([a-z0-9]+)(@(uw|washington|u\.washington)\.edu)?/g, '$1')
                .split(/[ ,]+/))
            : [];
    },

    _unique = function(array) {
        return $.grep(array, function(el, i) {
            return el.length > 0 && i === $.inArray(el, array);
        });
    },

    _enableCheckEligibility = function() {
        var $panel = $(location_hash),
            netids = _getNetidList();

        if (netids.length > 0) {
            $('#validate', $panel).removeAttr('disabled');
        } else {
            $('#validate', $panel).attr('disabled', 'disabled');
        }
    },

    _displayValidationResult = function(validated) {
        var $panel = $(location_hash),
            $table = $('.endorsed-netids-table table', $panel),
            $no_endorsements = $('.no-endorsements', $panel),
            source = $("#validated_content").html(),
            template = Handlebars.compile(source),
            row_source = $('#endorsee-row').html(),
            row_template = Handlebars.compile(row_source),
            context = {
                netids: {},
                netid_count: 0,
                netids_present: {},
                netids_present_count: 0,
                netid_errors: {},
                netid_error_count: 0
            };

        if ($no_endorsements.length && validated.validated.length) {
            $no_endorsements.addClass('visually-hidden');
        }

        $.each(validated.validated, function (endorsee_index) {
            var netid = this.netid,
                name = this.name,
                email = this.email,
                present = ($('.endorsed-netids-table tr[data-netid="' + netid + '"]', $panel).length > 0),
                $row,
                endorsement_count;

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

                endorsement_count = 0;
                $.each(this.endorsements, function (svc, endorsement) {
                    var row_html = row_template({
                        netid: netid,
                        name: name,
                        email: email,
                        service: svc,
                        endorsement: endorsement,
                        endorsee_index: endorsee_index,
                        endorsement_index: endorsement_count
                    });

                    Endorse.updateEndorsementForRowContext(endorsement);

                    if ($row) {
                        $row.before(row_html);
                    } else {
                        $('.endorsed-netids-table tbody').append(row_html);
                    }

                    endorsement_count += 1;
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

        // restripe table
        $('.endorsement_row_first', $table).each(function(index) {
            var netid = $(this).attr('data-netid');

            $('[data-netid='+ netid +']', $table)
                .removeClass('endorsee_row_even endorsee_row_odd')
                .addClass('endorsee_row_' + ((index % 2 === 0) ? 'even' : 'odd'));
        });
    },

    _validateUWNetids = function(netids) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
            $panel = $(location_hash);

        $.ajax({
            url: "/api/v1/validate/",
            type: "POST",
            data: JSON.stringify({ "netids": netids }),
            contentType: "application/json",
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
    };

    return {
        load: function () {
            _getEndorsedUWNetIDs();
            _registerEvents();
        }
    };
}());

export { ManageProvisionedServices };
