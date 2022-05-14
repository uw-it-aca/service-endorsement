// common service endorse javascript
/* jshint esversion: 6 */

import { Scroll } from "../scroll.js";
import { Button } from "../button.js";
import { Notify } from "../notify.js";

var ManageOfficeAccess = (function () {
    var content_id = 'office_access',
        location_hash = '#' + content_id,
        $panel = $(location_hash),
        $content = $('#office_access'),
        table_css = null,

        _registerEvents = function () {
            var $tab = $('.tabs div#access');

            // delegated events within our content
            $tab.on('endorse:MainTabExposed', function (e) {
                if (! $('.office-access-table', $panel).length) {
                    _getOfficeAccessUWNetIDs();
                }
            });

            $panel.on('click', '#add_access', function () {
                var netid = $('.inbox-netids', $panel).find(":selected").val();

                if (netid.length) {
                    _validateNetidAccessModal(netid);
                }
            }).on('input change', '.validate-netid-list textarea', function () {
                _enableCheckEligibility($(this));
            }).on('change', 'select.inbox-netids', function () {
                _scrollNetIDIntoView(this.value);
            }).on('change', 'select.office-access-types', function () {
                _setRenewUpdate($(this), this.value);
            }).on('click', '#validate_netids_access', function (e) {
                var mailbox = $('.validate-netid-list textarea').attr('data-mailbox'),
                    delegates = _getNetidList();

                Button.loading($('#' + this.id, $content));
                _validateOfficeAccessUWNetIDs(mailbox, delegates);
            }).on('click', '#access_provision', function (e) {
                var $button = $(this),
                    $row = $button.closest('tr');

                _confirmNetidAccessModal($row);
            }).on('click', '#access_revoke', function (e) {
                var $button = $(this),
                    $row = $button.closest('tr');

                _confirmNetidRevokeModal($row);
            }).on('click', '#access_renew', function (e) {
                var $button = $(this),
                    $row = $button.closest('tr');

                _confirmNetidRenewModal($row);
            }).on('click', '#access_update', function (e) {
                var $button = $(this),
                    $row = $button.closest('tr');

                _confirmNetidUpdateModal($row);
            }).on('endorse:OfficeDelegateConfirmation', function (e, context) {
                $panel.one('hidden.bs.modal', '#access_netids_modal', function() {
                    var $row = _accessTableRow(context.mailbox, context.delegate);

                    Button.loading($('#access_provision', $row));
                    _setAccessForDelegate(context);
                });
                _modalHide();
            }).on('endorse:OfficeDelegateRenew', function (e, context) {
                $panel.one('hidden.bs.modal', '#access_netids_modal', function() {
                    var $row = _accessTableRow(context.mailbox, context.delegate);

                    Button.loading($('#access_renew', $row));
                    _setAccessForDelegate(context);
                });
                _modalHide();
            }).on('endorse:OfficeDelegateRevoke', function (e, context) {
                $panel.one('hidden.bs.modal', '#access_netids_modal', function() {
                    $row = _accessTableRow(context.mailbox, context.delegate);

                    Button.loading($('#access_revoke', $row));
                    Button.disable($('#access_renew', $row));
                    _revokeAccessForDelegate(context);
                });
                _modalHide();
            }).on('endorse:OfficeDelegateUpdate', function (e, context) {
                $panel.one('hidden.bs.modal', '#access_netids_modal', function() {
                    var $row = _accessTableRow(context.mailbox, context.delegate);

                    Button.loading($('#access_update', $row));
                    _setAccessForDelegate(context);
                });
                _modalHide();
            }).on('endorse:OfficeDelegatableSuccess', function (e, data) {
                _displayOfficeAccessUWNetIDs(data.netids);
                _getOfficeAccessTypes();
            }).on('endorse:OfficeDelegatableFailure', function (e, data) {
                _displayOfficeAccessUWNetIDFailure(data);
            }).on('endorse:OfficeValidateNetIDsSuccess', function (e, data) {
                _modalHide();
                _displayValidatedUWNetIDs(data);
            }).on('endorse:OfficeValidateNetIDsFailure', function (e, data) {
                _modalHide();
                _displayValidateNetIDsFailure(data);
            }).on('endorse:OfficeDelegateAccessSuccess', function (e, accessee) {
                _updateOfficeAccessDisplay(accessee);
                _grantedNetidAccessModal(accessee);
            }).on('endorse:OfficeDelegateAccessFailure', function (e, accessee, error) {
                var $row = _accessTableRow(accessee.mailbox, accessee.name);

                Notify.error('Access error: ' + error);
                Button.reset($('#access_provision', $row));
            }).on('endorse:OfficeDelegateAccessSuccess', function (e, accessee) {
                _updateOfficeAccessDisplay(accessee);
                _grantedNetidAccessModal(accessee);
            }).on('endorse:OfficeDelegateAccessFailure', function (e, accessee, error) {
                var $row = _accessTableRow(accessee.mailbox, accessee.name);

                Notify.error('Access error: ' + error);
                Button.reset($('#access_provision', $row));
            }).on('endorse:OfficeDelegateRevokeSuccess', function (e, context) {
                _deleteOfficeAccessDisplay(context);
                _revokedNetidAccessModal(context);
            }).on('endorse:OfficeDelegateRevokeFailure', function (e, context, error) {
                var $row = _accessTableRow(context.mailbox, context.name);

                Notify.error('Revoke error: ' + error);
                Button.reset($('#access_revoke', $row));
                Button.enable($('#access_renew', $row));
            }).on('endorse:OfficeAccessTypesSuccess', function (e) {
                _displayOfficeAccessTypes();
            }).on('endorse:OfficeAccessTypesFailure', function (e, data) {
                alert('Cannot determine Access Types: ' + data);
            });
        },
        _showLoading = function () {
            var source = $("#access-loading").html(),
                template = Handlebars.compile(source);

            $content.html(template());
        },
        _displayOfficeAccessUWNetIDs = function (netids) {
            var source = $("#office_access_panel").html(),
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
                            mailbox: netid,
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
                        mailbox: netid,
                        name: name,
                        accessee_index: accessee_index,
                        access_index: 0
                    });
                }

                accessee_index += 1;
            });

            context.netids = unique_netids;

            $content.html(template(context));
            Scroll.init('.office-access-table');
        },
        _getOfficeAccessUWNetIDs = function() {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

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
            var context = {
                    mailbox: netid
                };

            _displayModal("#access_validate_netids_modal_content", context);
            $panel.one('shown.bs.modal', '#access_netids_modal', function() {
                $('textarea', $(this)).focus();
            });
        },
        _validateOfficeAccessUWNetIDs = function(mailbox, delegates) {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

            $.ajax({
                url: "/office/v1/validate",
                type: "POST",
                data: JSON.stringify({ "mailbox": mailbox, "delegates": delegates }),
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
        _displayValidatedUWNetIDs = function (validated) {
            var source = $("#office_access_row_partial").html(),
                template = Handlebars.compile(source),
                html;

            $.each(validated, function () {
                var mailbox = this.mailbox,
                    delegate = this.name,
                    $rows;

                if (!this.can_access) {
                    alert('Access by ' + delegate + ' is not available at this time.');
                    return true;
                }

                $rows = $('.office-access-table tr[data-mailbox="' + mailbox + '"]'),
                $rows.each(function (i) {
                    var $this_row = $(this),
                        row_delegate = $this_row.attr('data-delegate');

                    if (delegate == row_delegate) {
                        Notify.warning('Access for ' + row_delegate + ' already provided.');
                        return false;
                    } else if (delegate < row_delegate || i === $rows.length - 1) {
                        html = template({
                            mailbox: mailbox,
                            name: $('td.access-mailbox-name', $this_row).text(),
                            delegate: delegate,
                            accessee_index: $this_row.hasClass('endorsee_row_even') ? 0 : 1,
                            access_index: i});

                        if (delegate < row_delegate) {
                            $this_row.before(html);
                            if (i === 0) {
                                $this_row
                                    .removeClass('endorsement_row_first top-border')
                                    .addClass('endorsement_row_following hidden-names');
                            }
                        } else if ($this_row.hasClass('no-delegates')) {
                            $this_row.replaceWith(html);
                        } else {
                            $this_row.after(html);
                        }

                        _loadOfficeAccessTypeOptions(0, $('.access-type select',
                                                          _accessTableRow(mailbox, delegate)));
                        return false;
                    }
                });
            });
        },
        _displayValidateNetIDsFailure = function (data) {
            alert('Cannot validate at this time: ' + data);
        },
        _confirmNetidAccessModal = function ($row) {
            var context = {
                mailbox: $row.attr('data-mailbox'),
                delegate: $row.attr('data-delegate'),
                access_type: $('.access-type select option:selected', $row).val(),
                access_type_name: $('.access-type select option:selected', $row).text()
            };

            _displayModal("#confirm_netids_modal_content", context);
            $panel.one('shown.bs.modal', '#access_netids_modal', function(e) {
                $('button#confirm_netid_access').one('click', function(e) {
                    $panel.trigger('endorse:OfficeDelegateConfirmation', [context]);
                });
            })
        },
        _confirmNetidRevokeModal = function ($row) {
            var context = {
                mailbox: $row.attr('data-mailbox'),
                delegate: $row.attr('data-delegate'),
                access_type: $('.access-type select option:selected', $row).val(),
                access_type_name: $('.access-type select option:selected', $row).text()
            };

            _displayModal("#confirm_revoke_modal_content", context);
            $panel.one('shown.bs.modal', '#access_netids_modal', function(e) {
                $('button#confirm_netid_revoke').one('click', function(e) {
                    $panel.trigger('endorse:OfficeDelegateRevoke', [context]);
                });
            })
        },
        _confirmNetidRenewModal = function ($row) {
            var context = {
                mailbox: $row.attr('data-mailbox'),
                delegate: $row.attr('data-delegate'),
                access_type: $('.access-type select option:selected', $row).val(),
                access_type_name: $('.access-type select option:selected', $row).text()
            };

            _displayModal("#confirm_renew_modal_content", context);
            $panel.one('shown.bs.modal', '#access_netids_modal', function(e) {
                $('button#confirm_netid_renew').one('click', function(e) {
                    $panel.trigger('endorse:OfficeDelegateRenew', [context]);
                });
            })
        },
        _confirmNetidUpdateModal = function ($row) {
            var current_access_type = $('.access-type select', $row).attr('data-access-right-id'),
                context = {
                    mailbox: $row.attr('data-mailbox'),
                    delegate: $row.attr('data-delegate'),
                    access_type: current_access_type,
                    access_type_name: $('.access-type select option[value=' + current_access_type + ']', $row).text(),
                    new_access_type: $('.access-type select option:selected', $row).val(),
                    new_access_type_name: $('.access-type select option:selected', $row).text()
            };

            _displayModal("#confirm_update_modal_content", context);
            $panel.one('shown.bs.modal', '#access_netids_modal', function(e) {
                $('button#confirm_netid_update').one('click', function(e) {
                    $panel.trigger('endorse:OfficeDelegateUpdate', [context]);
                });
            })
        },
        _grantedNetidAccessModal = function (context) {
            _displayModal("#granted_netid_modal_content", context);
        },
        _revokedNetidAccessModal = function (context) {
            _displayModal("#revoked_netid_modal_content", context);
        },
        _displayModal = function (template_id, context) {
            var source = $(template_id).html(),
                template = Handlebars.compile(source);

            $('#access_netids_modal .modal-content', $content).html(template(context));
            _modalShow();
        },
        _modalShow = function () {
            $('#access_netids_modal', $content).modal('show');
        },
        _modalHide = function () {
            $('#access_netids_modal', $content).modal('hide');
        },
        _updateOfficeAccessDisplay = function (context) {
            var $row = _accessTableRow(context.mailbox, context.delegate);

            _updateOfficeAccessRow($row, context);
        },
        _updateOfficeAccessRow = function ($row, context) {
            var source = $("#office_access_row_partial").html(),
                template = Handlebars.compile(source),
                html;

            html = template({
                mailbox: context.mailbox,
                name: $('td.access-mailbox-name', $row).text(),
                delegate: context.delegate,
                status: 'Provisioned',
                accessee_index: $row.hasClass('endorsee_row_even') ? 0 : 1,
                access_index: $row.parent().children().index($row)});
            $row.replaceWith(html);
            $row = _accessTableRow(context.mailbox, context.delegate);
            _loadOfficeAccessTypeOptions(context.right_id,
                                         $('.office-access-types', $row));
        },
        _deleteOfficeAccessDisplay = function (context) {
            var selector = '.office-access-table tbody tr[data-mailbox="' + context.mailbox + '"]',
                mailbox_rows = -1,
                delete_row = -1,
                $delete_row;

            $(selector, $content).each(function () {
                var $row = $(this);

                mailbox_rows += 1;
                if ($row.attr('data-delegate') == context.delegate) {
                    delete_row = mailbox_rows;
                    $delete_row = $row;
                } else if ($delete_row) {
                    if (delete_row == 0) {
                        $row
                            .removeClass('endorsement_row_following')
                            .addClass('endorsement_row_first');
                    }

                    if ($row.hasClass('endorsee_row_even')) {
                        $row
                            .removeClass('endorsee_row_odd')
                            .addClass('endorsee_row_even');
                    } else {
                        $row
                            .removeClass('endorsee_row_even')
                            .addClass('endorsee_row_odd');
                    }
                }
            });

            if ($delete_row) {
                if (mailbox_rows == 0) {
                    var source = $("#office_access_row_partial").html(),
                        template = Handlebars.compile(source),
                        html = template({
                            mailbox: context.mailbox,
                            name: $('td.access-mailbox-name', $delete_row).text(),
                            accessee_index: $delete_row.hasClass('endorsee_row_even') ? 0 : 1,
                            access_index: 0});
                    $delete_row.replaceWith(html);
                } else {
                    $delete_row.remove();
                }
            }
        },
        _setAccessForDelegate = function (context) {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

            $.ajax({
                url: "/office/v1/access",
                type: "POST",
                data: JSON.stringify(context),
                contentType: "application/json",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    $panel.trigger('endorse:OfficeDelegateAccessSuccess', [results]);
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:OfficeDelegateAccessFailure', [context, error]);
                }
            });
        },
        _revokeAccessForDelegate = function (context) {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

            $.ajax({
                url: '/office/v1/access?mailbox=' + context.mailbox + '&delegate=' + context.delegate,
                type: 'DELETE',
                accepts: {html: 'application/json'},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    $panel.trigger('endorse:OfficeDelegateRevokeSuccess', [results]);
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:OfficeDelegateRevokeFailure', [context, error]);
                }
            });
        },
        _getNetidList = function ($textarea) {
            var netids = $('.validate-netid-list textarea').val(),
                netid_list = (netids) ? _unique(
                    netids.toLowerCase()
                        .replace(/\n/g, ' ')
                        .replace(/([a-z0-9]+)(@(uw|washington|u\.washington)\.edu)?/g, '$1')
                        .split(/[ ,]+/))
                        : [];

            if (netid_list.length) {
                $('.office-access-table td[data-mailbox]', $content).each(function () {
                    var mailbox = $(this).attr('data-mailbox'),
                        i;

                    i = netid_list.indexOf(mailbox);
                    if (i >= 0) {
                        netid_list.splice(i, 1);
                    }
                });
            }

            return netid_list;
        },
        _displayOfficeAccessTypes = function () {
            $(".office-access-types").each(function (){
                var $select = $(this),
                    right_id = $select.attr('data-access-right-id');

                _loadOfficeAccessTypeOptions(right_id, $select);
            });
        },
        _loadOfficeAccessTypeOptions = function (right_id, $select) {
            if (!right_id) {
                $('<option/>')
                    .text('-- Select --')
                    .val('')
                    .appendTo($select);
            }

            $.each(window.access.office.types, function (i, right) {
                var $option = $('<option/>')
                    .text(right.displayname)
                    .val(right.id);

                if (right_id == right.id) {
                    $option
                        .attr({'selected': 'selected'})
                        .css('font-weight: bold');
                }

                $option.appendTo($select);
            });
        },
        _getOfficeAccessTypes = function() {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

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
        _scrollNetIDIntoView = function (netid) {
            Scroll.scrollToNetid(netid, '.office-access-table');
        },
        _setRenewUpdate = function ($select, new_right_id) {
            var $row = $select.closest('tr'),
                $buttons = $select.closest('td').next('td'),
                right_id = $select.attr('data-access-right-id'),
                $provision_button = $('button#access_provision', $buttons),
                $renew_button = $('button#access_renew', $buttons),
                $revoke_button = $('button#access_revoke', $buttons),
                $update_button = $('button#access_update', $buttons),
                right_id = $select.attr('data-access-right-id');

            if ($('option:first', $select).val().length === 0) {
                if ($('option:selected', $select).val() != 0) {
                    Button.enable($provision_button);
                } else {
                    Button.disable($provision_button);
                }
            } else if (new_right_id === right_id) {
                Button.show($renew_button);
                Button.show($revoke_button);
                Button.hide($update_button);
            } else {
                Button.hide($renew_button);
                Button.hide($revoke_button);
                Button.show($update_button);
            }
        },
        _accessTableRow = function (netid, delegate) {
            var id = '.office-access-table tr[data-mailbox="' +
                netid + 
                '"][data-delegate="' + 
                delegate +
                '"]',
                $x = $(id, $content);
            return $x;
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
                $button.prop('disabled', false);
            } else {
                $button.prop('disabled', true);
            }
        };

    return {
        load: function () {
            _registerEvents();
        }
    };
}());

export { ManageOfficeAccess };
