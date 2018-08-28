// javascript to Manage Provisioned Services

var ManageProvisionedServices = {
    content_id: 'provisioned',
    location_hash: '#provisioned',

    load: function () {
        this._loadTab();
        this._registerEvents();
    },

    focus: function () {
        if (window.location.hash === this.location_hash) {
            $('a[href="' + this.location_hash + '"]').tab('show');
        }
    },

    _loadTab: function () {
        var tab_link_template = Handlebars.compile($("#provisioned-tab-link").html()),
            tab_content_template = Handlebars.compile($("#provisioned-tab-content").html()),
            context = {
                tab_content_id: ManageProvisionedServices.content_id
            };
        
        $('.nav-tabs').append(tab_link_template(context));
        $('.tab-content').append(tab_content_template(context));
    },

    _registerEvents: function () {
        // delegated events within our content
        $('.tab-pane#' + ManageProvisionedServices.content_id).on('click', 'button.confirm_revoke', function(e) {
            Revoke.revoke($(this), '#revoke_modal_content', 'endorse:UWNetIDsRevokeStatus');
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
        });

        // broader event scope
        $(document).on('shown.bs.tab', 'a[href="#' + ManageProvisionedServices.content_id + '"]', function (e) {
            ManageProvisionedServices._getEndorsedUWNetIDs();
        });
    },

    _getEndorsedUWNetIDs: function() {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
            $content = $('#' + ManageProvisionedServices.content_id);

        $content.html($('#endorsed-loading').html());

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
            $panel = $('div.tab-pane#' + ManageProvisionedServices.content_id);

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
            var $cols = $(this).find('td');

            if ($cols.length) {
                var row = [];

                $.each(fields, function(i, n) {
                    var $col = $($cols.get(n)),
                        provisioned = $col.attr('data-csv-provisioned'),
                        reason = $col.attr('data-csv-reason'),
                        endorsement,
                        context;

                    if (provisioned) {
                        context = provisioned.split('-');
                        endorsement = endorsed[context[1]] && endorsed[context[1]][context[0]];
                        if (endorsement) {
                            row.push((endorsement.datetime_endorsed) ? utc2local(endorsement.datetime_endorsed) : 'pending');
                        }
                    } else if (reason) {
                        context = reason.split('-');
                        endorsement = endorsed[context[1]] && endorsed[context[1]][context[0]];
                        if (endorsement) {
                            row.push(endorsement.reason);
                        }
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
