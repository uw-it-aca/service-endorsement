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
        _showLoading = function () {
            var $content = _contentDiv(),
                source = $("#access-loading").html(),
                template = Handlebars.compile(source);

            $content.html(template());
        },
        _getOfficeAccessUWNetIDs = function() {
            var $panel = $(location_hash);


            console.log('getting office access netids');
            $panel.trigger('endorse:OfficeDelegatableSuccess', {
                netids: {
                    a: {
                        name: 'netid a',
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
                    b: {
                        name: 'netid b',
                        delgates: [{
                            delegate: 'delegate3',
                            status: 'renew now',
                            type: 'full access and send as'
                        }]
                    }
                }
            });



        },
        _displayOfficeAccessUWNetIDs = function (netids) {
            var $content = _contentDiv(),
                source = $("#office-access-panel").html(),
                template = Handlebars.compile(source),
                context = {
                    access: []
                },
                accessee_index = 0;

            $.each(netids, function(netid) {
                var name = this.name;

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

            $content.html(template(context));
        },
        _displayOfficeAccessUWNetIDFailure = function (data) {
        },
        _registerEvents = function () {
            var $tab = $('.tabs div#access'),
                $panel = $(location_hash);

            // delegated events within our content
            $tab.on('endorse:MainTabExposed', function (e) {
                if (! $('.office-access-table', $panel).length) {
                    _showLoading();
                    _getOfficeAccessUWNetIDs();
                }
            });

            $panel.on('endorse:OfficeDelegatableSuccess', function (e, data) {
                _displayOfficeAccessUWNetIDs(data.netids);
            }).on('endorse:OfficeDelegatableFailure', function (e, data) {
                _displayOfficeAccessUWNetIDFailure(data);
            });
        };

    return {
        load: function () {
            _registerEvents();
        }
    };
}());

export { ManageOfficeAccess };
