// javascript to Manage Provisioned Services

var ManageProvisionedServices = {
    content_id: 'provisioned',
    location_hash: '#provisioned',

    load: function () {
        this._loadContent();
        this._registerEvents();
    },

    focus: function () {
        if (window.location.hash === this.location_hash) {
            $('a[href="' + this.location_hash + '"]').tab('show');
        }
    },

    _loadContent: function () {
        var content_template = Handlebars.compile($("#endorsed-netids").html()),
            context = {
                has_endorsed: false
            };
        
        $('#' + ManageProvisionedServices.content_id).append(content_template(context));
        ManageProvisionedServices._getEndorsedUWNetIDs();
    },

    _registerEvents: function () {
        $panel = $('#' + ManageProvisionedServices.content_id);

        // delegated events within our content
        $panel.on('click', 'button.confirm_endorse', function(e) {
            Endorse.endorse($(this), '#endorse_modal_content', 'endorse:UWNetIDsEndorseStatus');
        }).on('click', 'button.confirm_revoke', function(e) {
            Revoke.revoke($(this), '#revoke_modal_content', 'endorse:UWNetIDsRevokeStatus');
        }).on('click', 'button.confirm_renew', function(e) {
            Renew.renew($(this), '#renew_modal_content', 'endorse:UWNetIDsRenewStatus');
        }).on('click', '#export_csv', function (e) {
            ManageProvisionedServices._exportProvisionedToCSV();
        }).on('endorse:UWNetIDsEndorsed', function (e, endorsed) {
            $('button#confirm_endorsements').button('reset');
            ManageProvisionedServices._displayEndorsedUWNetIDs(endorsed);
            window.endorsed = endorsed;
        }).on('endorse:UWNetIDsEndorsedError', function (e, error) {
            $('#' + ManageProvisionedServices.content_id).html($('#endorsed-failure').html());
        }).on('endorse:UWNetIDsRevokeStatus', function (e, data) {
            $.each(data.revokees, function (netid, endorsements) {
                $.each(endorsements, function (endorsement, state) {
                    var id = endorsement + '-' + netid;

                    $('.reason-' + id).html('');
                    $('.revoke-' + id).html('');
                    $('.endorsed-' + id).html($("#unendorsed").html());
                });
            });
        }).on('endorse:UWNetIDsRenewStatus', function (e, data) {
            $.each(data.renewees, function (netid, endorsements) {
                $.each(endorsements, function (endorsement, state) {
                    var id = endorsement + '-' + netid;

                    $('.reason-' + id).html('');
                    $('.revoke-' + id).html('');
                    $('.endorsed-' + id).html($("#unendorsed").html());
                });
            });
        }).on('change', 'select.display-filter', function(e) {
            var display = $(this).find('option:selected').val(),
                $rows = $panel.find('table tr td .row');

            if (display === 'all') {
                $rows.removeClass('visually-hidden');
            } else {
                $rows.addClass('visually-hidden');
                $panel.find('table tr td .row.' + display + '_service').removeClass('visually-hidden');
            }
        });
    },

    _getEndorsedUWNetIDs: function() {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
            $content = $('#' + ManageProvisionedServices.content_id);

        $('.loading', $content).html($('#endorsed-loading').html());

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
                if (endorsement.datetime_endorsed) {
                    var now = moment(),
                        provisioned = moment(endorsement.datetime_endorsed),
                        expires = moment(endorsement.datetime_endorsed).add(365, 'days'),
                        expiring = moment(endorsement.datetime_endorsed).add(30, 'days');

                    this.expires = expires.format('M/D/YYYY')
                    this.expires_relative = expires.fromNow()
                    
                    if (now.isBetween(expiring, expires)) {
                        this.expiring = this.expires;
                    }

                    if (now.isAfter(expires)) {
                        this.expired = this.expires;
                    }
                }
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
