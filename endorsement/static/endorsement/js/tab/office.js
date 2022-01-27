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
            }).on('endorse:OfficeDelegatableFailure', function (e, data) {
                _displayOfficeAccessUWNetIDFailure(data);
            }).on('endorse:OfficeValidateNetIDsSuccess', function (e, data) {
                $('#validate_netids_modal', _contentDiv()).modal('hide');
                _displayValidatedUWNetIDs(data.netids);
            }).on('endorse:OfficeValidateNetIDsFailure', function (e, data) {
                $('#validate_netids_modal', _contentDiv()).modal('hide');
                _displayValidateNetIDsFailure(data);
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

                $.each(this.delgates, function(index) {
                    var row = {
                        netid: netid,
                        name: name,
                        delegate: this.delegate,
                        status: this.status,
                        type: this.type,
                        accessee_index: accessee_index,
                        access_index: index
                    };

                    context.access.push(row);
                });

                accessee_index += 1;
            });

            context.netids = unique_netids;

            $content.html(template(context));
        },
        _getOfficeAccessUWNetIDs = function() {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
                $panel = $(location_hash);

            _showLoading();

            setTimeout(function(){


            $panel.trigger('endorse:OfficeDelegatableSuccess', {
                netids: {
                    javerage: {
                        name: 'John Average',
                        delgates: [{
                            delegate: 'delegate1',
                            status: 'renew by whenever',
                            type: 'full access and send as'
                        },{
                            delegate: 'delegate2',
                            status: 'renew at your leasure',
                            type: 'full access and send as'
                        }]
                    },
                    uxrecruitment: {
                        name: 'AXDD UX',
                        delgates: [{
                            delegate: 'delegate3',
                            status: 'renew now',
                            type: 'full access and send as'
                        }]
                    }
                }
            });

            }, 500);
            return;

            $.ajax({
                url: "/api/v1/delegate/",
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

            setTimeout(function(){

            var netids_list = netids;

            $panel.trigger('endorse:OfficeValidateNetIDsSuccess', {
                netids: netid_list
            });

            }, 500);

            return;

            $.ajax({
                url: "/api/v1/validate/",
                dataType: "JSON",
                type: "GET",
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
