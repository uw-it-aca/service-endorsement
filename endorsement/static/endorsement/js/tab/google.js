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

            $tab.on('endorse:drivesTabExposed', function (e) {
                if ($content.is(':empty')) {
                    _getSharedDrives();
                }
            });

            $panel.on('change', 'select#shared_drive_action', function (e) {
                var $this = $(this),
                    action = $(this).val(),
                    drive_id = $this.attr('data-drive-id'),
                    itbill_url = $this.attr('data-itbill-url');

                if (action === 'shared_drive_accept') {
                    _sharedDriveAcceptModal(drive_id, itbill_url);
                } else if (action === 'shared_drive_change') {
                    // below will indirect to itbill thru "you are leaving" modal
                    // _sharedDriveChangeModal(drive_id, itbill_url);
                    // below will request the url directly
                    _getITBill_URL($(this).attr('data-drive-id'));
                    // below opens a simple window
                    //window.open(itbill_url, 'ITBill', 'directories=no,titlebar=no,toolbar=no,location=no,status=no,menubar=no,scrollbars=no,resizable=no,width=800,height=800');
                } else if (action === 'shared_drive_revoke') {
                    _sharedDriveRevokeModal(drive_id);
                }
            }).delegate('#shared_drive_accept', 'click', function (e) {
                _displayModal('#shared-drive-acceptance', {
                    drive_id: $(this).attr('data-drive-id')});
            }).delegate('#confirm_itbill_visit', 'click', function (e) {
                _getITBill_URL($(this).attr('data-drive-id'));
            }).delegate('#confirm_itbill_form_finished', 'click', function (e) {
                _modalHide();
            }).delegate('#confirm_shared_drive_acceptance', 'click', function (e) {
                _setSharedDriveResponsibility($(this).attr('data-drive-id'), true);
            }).delegate('#confirm_shared_drive_revoke', 'click', function (e) {
                _setSharedDriveResponsibility($(this).attr('data-drive-id'), false);
            }).delegate('#refresh_drive', 'click', function (e) {
                e.preventDefault();
                _refreshSharedDrive($(this).attr('data-drive-id'));
            }).on('endorse:SharedDriveRefresh', function (e, data) {
                _updateSharedDrivesDisplay(data.drives[0]);
            }).on('endorse:SharedDriveRefreshError', function (e, error) {
                Notify.error('Sorry, but subscription information unavailable at this time: ' + error);
            }).on('endorse:SharedDriveResponsibilityAccepted', function (e, data) {
                var drive = (data.drives && data.drives.length === 1) ? data.drives[0] : null;

                if (!drive) {
                    Notify.error('Error retrieving renewal result.');
                    return;
                }

                _modalHide();
                _updateSharedDrivesDisplay(drive);
                Notify.success('Shared drive "' + drive.drive.drive_name + '" provision renewed.', 10000);
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
            }).on('hide.bs.modal', function () {
                var $modal_body = $('.modal-body.itbill-form-modal');

                if ($modal_body.length) {
                    var drive_id = $modal_body.attr('data-drive-id'),
                        drive_name = $modal_body.attr('data-drive-name');

                    _refreshSharedDrive(drive_id);
                }
            }).on('hidden.bs.modal', function () {
                $('select[data-drive-id]', $content).val('select');
            }).on('endorse:SharedDrivesSuccess', function (e, data) {
                _displaySharedDrives(data.drives);
            }).on('endorse:SharedDrivesFailure', function (e, data) {
                _displaySharedDrivesFailure(data);
            }).on('endorse:SharedDrivesITBIllURLSuccess', function (e, data) {
                var url = (data.hasOwnProperty('drives') && data.drives.length == 1) ? data.drives[0].itbill_form_url : null;

                if (url) {
                    _ITBillFormModal(data.drives[0]);
                } else {
                    Notify.error('Sorry, but we cannot retrieve the ITBill Form URL at this time.');
                }
            }).on('endorse:SharedDrivesITBIllURLFailure', function (e, data) {
                _modalHide();
                Notify.error('Sorry, but we cannot retrieve the ITBill URL at this time: ' + data);
            }).popover({
                selector: 'span.prt-data-popover',
                trigger: 'focus',
                html: true
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
        _updateSharedDrivesDisplay = function (record) {
            var source = $("#shared_drives_row_partial").html(),
                template = Handlebars.compile(source);

            if ($('tr[data-drive-id="' + record.drive.drive_id + '"]').attr('data-thumb-print') == record.thumb_print) {
                return;
            }

            _prepSharedDriveContext(record);

            $('tr.shared-drive-row[data-drive-id="' + record.drive.drive_id + '"]').replaceWith(template(record));
            $('tr.shared-drive-row[data-drive-id="' + record.drive.drive_id + '"]').addClass('itbill_updated');
            Notify.success('"' + record.drive.drive_name + '" updated', 10000);
        },
        _displaySharedDrives = function (drives) {
            var source = $("#shared_drives_panel").html(),
                template = Handlebars.compile(source);

            if (drives.length === 0) {
                source = $("#no_shared_drives").html();
                template = Handlebars.compile(source);
                $content.html(template());
                return;
            }

            // convert drives data into context-appropriate values
            $.each(drives, function (i, drive) {
                _prepSharedDriveContext(drive);
            });

            $content.html(template({drives: drives}));
            Scroll.init('.shared-drives-table');
        },
        _prepSharedDriveContext = function (drive) {
            var expiration = moment(drive.datetime_expiration),
                deadline = moment(drive.datetime_subscription_deadline),
                now = moment.utc();

            drive.expiration_date = expiration.format('M/D/YYYY');
            drive.expiration_days = expiration.diff(now, 'days');
            drive.expiration_from_now = expiration.from(now);

            drive.subscription_deadline_date = deadline.format('M/D/YYYY');
            drive.subscription_deadline_from_now = deadline.from(now);

            //drive.in_flight = (drive.subscription && drive.subscription.query_priority === 'high');
            drive.valid_subscription = (drive.subscription && !['draft', 'closed', 'cancelled'].includes(drive.subscription.state));
            drive.requires_subscription = !(drive.drive.drive_quota.is_subsidized || drive.valid_subscription);
            drive.quota_notes = [{
                is_capped: (!["uw.edu", "None"].includes(drive.drive.drive_quota.org_unit_name) && drive.drive.drive_usage > drive.drive.drive_quota.quota_limit)
            }];

            if (drive.subscription) {
                $.each(drive.subscription.provisions, function () {
                    $.each(this.quantities, function () {
                        var starting = this.start_date ? moment(this.start_date) : null,
                            ending = this.end_date ? moment(this.end_date): null,
                            is_future = starting && starting.diff(now) > 0,
                            is_ending = starting && ending && starting.diff(now) < 0 && ending.diff(now) > 0,
                            is_increasing = this.quota_limit > drive.drive.drive_quota.quota_limit,
                            is_decreasing = this.quota_limit < drive.drive.drive_quota.quota_limit,
                            is_changing = (is_future || is_ending);

                        drive.quota_notes.push({
                            is_future: is_future,
                            is_ending: is_ending,
                            quota_limit: this.quota_limit,
                            is_increasing: is_increasing && is_future,
                            is_decreasing: is_decreasing && is_future,
                            is_changing: is_changing,
                            start_date: moment(this.start_date).format('M/D/YYYY'),
                            end_date: moment(this.end_date).format('M/D/YYYY')
                        });
                    });
                });
            }
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
        _refreshSharedDrive = function (drive_id) {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

            $.ajax({
                url: "/google/v1/shared_drive/" + drive_id + "/?refresh=1",
                type: "GET",
                contentType: "application/json",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    $panel.trigger('endorse:SharedDriveRefresh', [results]);
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:SharedDriveRefreshError', [error]);
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
        _ITBillFormModal = function (drive) {
            _displayModal('#shared-drive-itbill-form-modal', {
                drive: drive
            }, {
                modal_size: 'modal-xl',
                backdrop: 'static',
                keyboard: false
            });
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
        _displayModal = function (template_id, context, options) {
            var source = $(template_id).html(),
                template = Handlebars.compile(source),
                $modal = $('#shared_drive_modal'),
                $dialog = $('div.modal-dialog', $dialog),
                modal_options = options || {};

            // reset options
            $dialog.removeClass('modal-sm modal-lg modal-xl');
            if (modal_options.hasOwnProperty('modal_size')) {
                $dialog.addClass(modal_options.modal_size);
            }

            $('#shared_drive_modal .modal-content', $content).html(template(context));

            modal_options.show = true;
            $('#shared_drive_modal', $content).modal(modal_options);
        },
        _modalHide = function () {
            var $modal = $('#shared_drive_modal', $content);

            $modal.modal('hide');
            $modal.data('bs.modal', null);
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
