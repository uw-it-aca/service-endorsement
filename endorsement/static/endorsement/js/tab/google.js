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
                _getSharedDrives();
            });

            $panel.on('change', 'select#shared_drive_action', function (e) {
                var $this = $(this),
                    action = $(this).val(),
                    drive_id = $this.attr('data-drive-id'),
                    itbill_url = $this.attr('data-itbill-url');

                if (action === 'shared_drive_accept') {
                    _sharedDriveAcceptModal(drive_id, itbill_url);
                } else if (action === 'shared_drive_change') {
                    _sharedDriveChangeModal(drive_id, itbill_url);
                } else if (action === 'shared_drive_revoke') {
                    _sharedDriveRevokeModal(drive_id);
                }
            }).on('click', '#shared_drive_accept', function (e) {
                _displayModal('#shared-drive-acceptance', {
                    drive_id: $(this).attr('data-drive-id')});
            }).on('click', '#confirm_itbill_visit', function (e) {
                var $this = $(this),
                    itbill_url = $this.attr('data-itbill-url'),
                    drive_id = $this.attr('data-drive-id');

                if (itbill_url) {
                    window.open(itbill_url, '_blank');
                } else {
                    _getITBill_URL(drive_id);
                }

                _modalHide();
            }).on('click', '#confirm_shared_drive_acceptance', function (e) {
                _setSharedDriveResponsibility($(this).attr('data-drive-id'), true);
            }).on('click', '#confirm_shared_drive_revoke', function (e) {
                _setSharedDriveResponsibility($(this).attr('data-drive-id'), false);
            }).on('endorse:SharedDriveResponsibilityAccepted', function (e, data) {
                _modalHide();
                _updateSharedDrivesDiplay(data.drives[0]);
            }).on('endorse:SharedDriveResponsibilityAcceptedError', function (e, error) {
                Notify.error('Sorry, but we cannot accept responsibility at this time: ' + error);
            }).on('change', '#shared_drive_modal input', function () {
                var $modal = $(this).closest('#shared_drive_modal'),
                    $accept_button = $('button.accept-button', $modal),
                    $checkboxes = $('input.accept-button-dependency', $modal),
                    checked = 0;

                $checkboxes.each(function () {
                    if (this.checked)
                        checked += 1;
                });

                if ($checkboxes.length === checked && $('.error').length === 0) {
                    $accept_button.removeAttr('disabled');
                } else {
                    $accept_button.attr('disabled', 'disabled');
                }
            }).on('hidden.bs.modal', function () {
                $('select[data-drive-id]', $content).val('select');
            }).on('endorse:SharedDrivesSuccess', function (e, data) {
                _displaySharedDrives(data.drives);
            }).on('endorse:SharedDrivesFailure', function (e, data) {
                _displaySharedDrivesFailure(data);
            }).on('endorse:SharedDrivesITBIllURLSuccess', function (e, data) {
                debugger
                window.open(data.subscription.url, '_blank');
            }).on('endorse:SharedDrivesITBIllURLFailure', function (e, data) {
                Notify.error('Sorry, but we cannot retrieve the ITBill URL at this time: ' + data);
            });

            $(document).on('endorse:TabChange', function (e, data) {
                if (data == 'drives') {
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
        _updateSharedDrivesDiplay = function (record) {
            var source = $("#shared_drives_row_partial").html(),
                template = Handlebars.compile(source),
                $row = $('tr.shared-drive-row[data-drive-id="' + record.drive.drive_id + '"]');

            _prepSharedDriveContext(record);

            $row.replaceWith(template(record));
        },
        _displaySharedDrives = function (drives) {
            var source = $("#shared_drives_panel").html(),
                template = Handlebars.compile(source);

            if (drives.length === 0) {
                source = $("#no_shared_drives").html();
                template = Handlebars.compile(source),
                $content.html(template());
                return;
            }

            // convert drives data into context-appropriate values
            $.each(drives, function (i, drive) {
                _prepSharedDriveContext(drive);
            });

            $content.html(template({drives: drives}));
            Scroll.init('.shared-drives-table');
            $('[data-toggle="popover"]').popover();
        },
        _prepSharedDriveContext = function (drive) {
            var expiration = moment(drive.datetime_expiration),
                days_remaining = expiration.diff(now, 'days'),
                now = moment.utc();

            drive.expiration_date = expiration.format('M/D/YYYY');
            drive.expiration_days = expiration.diff(now, 'days');
            drive.expiration_from_now = expiration.from(now);
        },
        _getSharedDrives = function() {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

            _showLoading();

            $.ajax({
                url: "/google/v1/shared_drive/",
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
        _setSharedDriveResponsibility = function (drive_id, accepted) {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

            $.ajax({
                url: "/google/v1/shared_drive/" + drive_id,
                type: "PUT",
                data: JSON.stringify({accept: accepted}),
                contentType: "application/json",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    $panel.trigger('endorse:SharedDriveResponsibilityAccepted', [results]);
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:SharedDriveResponsibilityAcceptedError', [error]);
                }
            });
        },
        _getITBill_URL = function (drive_id) {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

            $.ajax({
                url: "/google/v1/shared_drive/" + drive_id + "/itbill_url/",
                dataType: "JSON",
                type: "GET",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    $panel.trigger('endorse:SharedDrivesITBIllURLSuccess', [results]);
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:SharedDrivesITBIllURLFailure', [error]);
                }
            });
        },
        _displaySharedDrivesFailure = function (data) {
            Notify.error('Sorry, but we cannot retrieve shared drive information at the time: ' + data);
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
        },
        _sharedDriveAcceptModal = function (drive_id, itbill_url) {
            _displayModal('#shared-drive-acceptance', {
                drive_id: drive_id,
                itbill_url: itbill_url
            });
        },
        _sharedDriveChangeModal = function (drive_id, itbill_url) {
            _displayModal('#shared-drive-visit-itbill', {
                drive_id: drive_id,
                itbill_url: itbill_url
            });
        },
        _sharedDriveRevokeModal = function (drive_id) {
            _displayModal('#shared-drive-revoke', {
                drive_id: drive_id,
            });
        },
        _displayModal = function (template_id, context) {
            var source = $(template_id).html(),
                template = Handlebars.compile(source);

            $('#shared_drive_modal .modal-content', $content).html(template(context));
            _modalShow();
        },
        _modalShow = function () {
            $('#shared_drive_modal', $content).modal('show');
        },
        _modalHide = function () {
            $('#shared_drive_modal', $content).modal('hide');
            $('body').removeClass('modal-open');
            $('.modal-backdrop').remove();
        };

    return {
        load: function () {
            _registerEvents();
            _showTab();
        }
    };
}());

export { ManageSharedDrives };
