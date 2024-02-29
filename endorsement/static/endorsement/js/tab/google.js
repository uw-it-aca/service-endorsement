// common service endorse javascript
/* jshint esversion: 6 */

import { Scroll } from "../scroll.js";
import { Button } from "../button.js";
import { Notify } from "../notify.js";
import { DateTime } from "../datetime.js";
import { History } from "../history.js";

var ManageSharedDrives = (function () {
    var content_id = 'shared_drives',
        location_hash = '#' + content_id,
        $panel = $(location_hash),
        $content = $(location_hash),

        _registerEvents = function () {
            var $tab = $('.tabs div#drives');

            // delegated events within our content
            $tab.on('endorse:drivesTabExposed', function (e) {
                var $drives_table = $('.shared-drive-table', $panel);

                _getSharedDrives();
            });

            $panel.on('endorse:SharedDrivesSuccess', function (e, data) {
                _displaySharedDrives(data.drives);
            }).on('endorse:SharedDrivesFailure', function (e, data) {
                _displaySharedDrivesFailure(data);
            });

            $(document).on('endorse:TabChange', function (e, data) {
                if (data == 'access') {
                    _adjustTabLocation();
                }
            }).on('endorse:HistoryChange', function (e) {
                _showTab();
            });
        },
        _showLoading = function () {
            var source = $("#shared-drives-loading").html(),
                template = Handlebars.compile(source);

            $content.html(template());
        },
        _displaySharedDrives = function (drives) {
            var source = $("#shared_drives_panel").html(),
                template = Handlebars.compile(source);

            $content.html(template({drives: drives}));
            Scroll.init('.shared-drives-table');
            $('[data-toggle="popover"]').popover();
        },
        _getSharedDrives = function() {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

            _showLoading();

            $.ajax({
                url: "/google/v1/shared_drives",
                dataType: "JSON",
                type: "GET",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    $panel.trigger('endorse:SharedDrivesSuccess', [results]);
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:SharedDrivesFailure', [error]);
                }
            });
        },
        _displaySharedDrivesFailure = function (data) {
            alert('Sorry, but we cannot retrieve shared drive information at the time: ' + data);
        },
        _adjustTabLocation = function (tab) {
            History.addPath('drives');
        },
        _showTab = function () {
            if (window.location.pathname.match(/\/drives$/)) {
                setTimeout(function(){
                    $('.tabs .tabs-list li[data-tab="drives"] span').click();
                },100);
            }
        };

    return {
        load: function () {
            _registerEvents();
            _showTab();
        }
    };
}());

export { ManageSharedDrives };
