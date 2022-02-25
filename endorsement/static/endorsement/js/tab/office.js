// common service endorse javascript
/* jshint esversion: 6 */

var ManageOfficeAccess = (function () {
    var content_id = 'office_access',
        location_hash = '#' + content_id,
        table_css = null,

        _contentDiv = function () {
            var $panel = $(location_hash);

            return $('#office_access')
        },
        _registerEvents = function () {
            var $tab = $('.tabs div#access'),
                $panel = $(location_hash);

            // delegated events within our content
            $tab.on('endorse:MainTabExposed', function (e) {
                if (! $('.office-access-table', $panel).length) {
                    _getOfficeAccessUWNetIDs();
                }
            });

            $panel.on('click', '#add_access', function () {
                var netid = $('.inbox_netids', $panel).find(":selected").val();

                if (netid.length) {
                    _validateNetidAccessModal(netid);
                }
            }).on('input change', '.validate_netid_list textarea', function () {
                _enableCheckEligibility($(this));
            }).on('click', '#validate_netids_access', function (e) {
                var netids = _getNetidList();

                $('.office-access-table tbody .endorsed-netid', _contentDiv()).each(function () {
                    var mailbox = $(this).html(),
                        i;

                    i = netids.indexOf(mailbox);
                    if (i >= 0) {
                        netids.splice(i, 1);
                    }
                }); 

                debugger

                // complain if one already exists or just exclude it?

                _validateOfficeAccessUWNetIDs(netids);
            }).on('endorse:OfficeDelegatableSuccess', function (e, data) {
                _displayOfficeAccessUWNetIDs(data.netids);
                _getOfficeAccessTypes();
            }).on('endorse:OfficeDelegatableFailure', function (e, data) {
                _displayOfficeAccessUWNetIDFailure(data);
            }).on('endorse:OfficeValidateNetIDsSuccess', function (e, data) {
                $('#validate_netids_modal', _contentDiv()).modal('hide');
                _displayValidatedUWNetIDs(data.netids);
            }).on('endorse:OfficeValidateNetIDsFailure', function (e, data) {
                $('#validate_netids_modal', _contentDiv()).modal('hide');
                _displayValidateNetIDsFailure(data);
            }).on('endorse:OfficeAccessTypesSuccess', function (e) {
                _displayOfficeAccessTypes();
            }).on('endorse:OfficeAccessTypesFailure', function (e, data) {
                alert('Cannot determine Access Types: ' + data);
            });
        },
        _showLoading = function () {
            var $content = _contentDiv(),
                source = $("#access-loading").html(),
                template = Handlebars.compile(source);

            $content.html(template());
        },
        _displayOfficeAccessUWNetIDs = function (netids) {
            var $content = _contentDiv(),
                source = $("#office-access-panel").html(),
                template = Handlebars.compile(source),
                context = {
                    access: []
                },
                unique_netids = [],
                accessee_index = 0;


            $.each(netids, function(netid) {
                var name = this.name;

                if (unique_netids.indexOf(netid) < 0) {
                    unique_netids.push(netid);
                }

                if (this.access.length > 0) {
                    $.each(this.access, function(i, d) {
                        context.access.push({
                            netid: netid,
                            name: name,
                            delegate: d.delegate,
                            status: d.status,
                            right_id: d.right_id,
                            accessee_index: accessee_index,
                            access_index: i
                        });
                    });
                } else {
                    context.access.push({
                        netid: netid,
                        name: name,
                        accessee_index: accessee_index,
                        access_index: 0
                    });
                }

                accessee_index += 1;
            });

            context.netids = unique_netids;

            $content.html(template(context));
        },
        _getOfficeAccessUWNetIDs = function() {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
                $panel = $(location_hash);

            _showLoading();

            $.ajax({
                url: "/office/v1/access",
                dataType: "JSON",
                type: "GET",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    $panel.trigger('endorse:OfficeDelegatableSuccess', [results]);
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:OfficeDelegatableFailure', [error]);
                }
            });
        },
        _displayOfficeAccessUWNetIDFailure = function (data) {
            alert('Sorry, but we cannot retrieve mailbox netids at the moment: ' + data);
        },
        _validateNetidAccessModal = function (netid) {
            var source = $("#access_validate_netids_modal_content").html(),
                template = Handlebars.compile(source),
                $modal = $('#validate_netids_modal', _contentDiv()),
                context = {
                    netid: netid
                };

            $('.modal-content', $modal).html(template(context));
            $modal.modal('show');
        },
        _validateOfficeAccessUWNetIDs = function(netids) {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
                $panel = $(location_hash);

            //show loading on button

            $.ajax({
                url: "/office/v1/validate",
                type: "POST",
                data: JSON.stringify({ "netids": netid_list }),
                contentType: "application/json",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    $panel.trigger('endorse:OfficeValidateNetIDsSuccess', [results]);
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:OfficeValidateNetIDsFailure', [error]);
                }
            });
        },
        _displayValidatedUWNetIDs = function (netids) {
            alert('insert validated netids into table');
        },
        _displayValidateNetIDsFailure = function (data) {
            alert('Cannot validate at this time: ' + data);
        },
        _getNetidList = function ($textarea) {
            var netid_list = $('.validate_netid_list textarea').val();

            return (netid_list) ? _unique(
                netid_list.toLowerCase()
                    .replace(/\n/g, ' ')
                    .replace(/([a-z0-9]+)(@(uw|washington|u\.washington)\.edu)?/g, '$1')
                    .split(/[ ,]+/))
                : [];
        },
        _displayOfficeAccessTypes = function () {
            $(".office-access-types").each(function (){
                var $select = $(this),
                    right_id = $select.attr('data-access-right-id');

                _loadOfficeAccessTypeOptions(right_id, $select);
            });
        },
        _loadOfficeAccessTypeOptions = function (right_id, $select) {
            $('<option/>').text('Choose...').appendTo($select);
            $.each(window.access.office.types, function (i, right) {
                var $option = $('<option/>')
                    .text(right.displayname)
                    .val(right.id);

                if (right_id == right.id) {
                    $option.attr({'selected': 'selected'});
                }

                $option.appendTo($select);
            });
        },
        _getOfficeAccessTypes = function() {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
                $panel = $(location_hash);

            $.ajax({
                url: "/office/v1/access/rights",
                dataType: "JSON",
                type: "GET",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    window.access.office.types = results
                    $panel.trigger('endorse:OfficeAccessTypesSuccess');
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:OfficeAccessTypesFailure', [error]);
                }
            });
        },
        _unique = function(array) {
            return $.grep(array, function(el, i) {
                return el.length > 0 && i === $.inArray(el, array);
            });
        },
        _enableCheckEligibility = function() {
            var netids = _getNetidList(),
                $button = $('button#validate_netids_access');

            if (netids.length > 0) {
                $button.removeAttr('disabled');
            } else {
                $button.attr('disabled', 'disabled');
            }
        };
;

    return {
        load: function () {
            _registerEvents();
        }
    };
}());

export { ManageOfficeAccess };
