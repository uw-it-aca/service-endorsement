// common service endorse javascript
/* jshint esversion: 6 */

import { Scroll } from "../scroll.js";
import { Button } from "../button.js";
import { Notify } from "../notify.js";
import { DateTime } from "../datetime.js";
import { History } from "../history.js";

var ManageOfficeAccess = (function () {
    var content_id = 'office_access',
        location_hash = '#' + content_id,
        $panel = $(location_hash),
        $content = $('#office_access'),

        _registerEvents = function () {
            var $tab = $('.tabs div#access');

            // delegated events within our content
            $tab.on('endorse:accessTabExposed', function (e) {
                var $access_table = $('.office-access-table', $panel);

                if ($access_table.length) {
                    $access_table.remove();
                }

                _getOfficeAccessUWNetIDs();
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
            }).on('click', 'input.access-conflict', function (e) {
                var $this = $(this),
                    $button = $this.closest('div.row').find('button#access_resolve');

                $button.prop('disabled', false);
            }).on('click', 'button#access_resolve', function (e) {
                var $this = $(this),
                    $checked = $this.closest('div.row').find('input.access-conflict:checked'),
                    mailbox = $this.attr('data-mailbox'),
                    delegate = $this.attr('data-delegate'),
                    right = $checked.val();

                _resolveAccessConflict(mailbox, delegate,right);
            }).on('click', 'button#confirm_resolved_conflict', function (e) {
                _modalHide();
                $('.tabs div#access').trigger('endorse:accessTabExposed');
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
                    var $row = _accessTableRow(context.mailbox, context.delegate);

                    Button.loading($('#access_revoke', $row));
                    Button.disable($('#access_renew', $row));
                    _revokeAccessForDelegate(context);
                });
                _modalHide();
            }).on('endorse:OfficeDelegateUpdate', function (e, context) {
                $panel.one('hidden.bs.modal', '#access_netids_modal', function() {
                    var $row = _accessTableRow(context.mailbox, context.delegate);

                    Button.loading($('#access_update', $row));
                    _updateAccessForDelegate(context);
                });
                _modalHide();
            }).on('endorse:OfficeDelegatableSuccess', function (e, data) {
                _displayOfficeAccessDelegatable(data.netids);
                _getOfficeAccessTypes($panel);
            }).on('endorse:OfficeDelegatableFailure', function (e, data) {
                _displayOfficeAccessUWNetIDFailure(data);
            }).on('endorse:OfficeValidateNetIDsSuccess', function (e, data) {
                _modalHide();
                $('select.inbox-netids', $content).val('');
                _displayValidatedUWNetIDs(data);
            }).on('endorse:OfficeValidateNetIDsFailure', function (e, data) {
                _modalHide();
                _displayValidateNetIDsFailure(data);
            }).on('endorse:OfficeDelegateAccessSuccess', function (e, context) {
                _updateOfficeAccessDisplay(context);
                _grantedNetidAccessModal(context);
            }).on('endorse:OfficeDelegateAccessFailure', function (e, accessee, error) {
                var $row = _accessTableRow(accessee.mailbox, accessee.delegate);

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

            }).on('endorse:OfficeAccessResolveSuccess', function (e, data) {
                _resolvedAccessModal(data);
            }).on('endorse:OfficeAccessResolveFailure', function (e, data) {
                alert('Access Resolution failure: ' + data);
            }).on('endorse:OfficeAccessTypesSuccess', function (e) {
                _displayOfficeAccessTypes();
            }).on('endorse:OfficeAccessTypesFailure', function (e, data) {
                alert('Cannot determine Access Types: ' + data);
            });

            $(document).on('endorse:TabChange', function (e, data) {
                if (data == 'access') {
                    _adjustTabLocation();
                }
            }).on('change', '#access_netids_modal input', function () {
                var $modal = $(this).closest('#access_netids_modal'),
                $accept_button = $('button#confirm_netid_access', $modal),
                $checkboxes = $('input.accept_responsibility', $modal),
                checked = 0;

                $checkboxes.each(function () {
                    if (this.checked)
                        checked += 1;
                });

                // accept all inputs and no "errors"
                if ($checkboxes.length === checked && $('.error').length === 0) {
                    $accept_button.removeAttr('disabled');
                } else {
                    $accept_button.attr('disabled', 'disabled');
                }
            }).on('endorse:HistoryChange', function (e) {
                _showTab();
            });
        },
        _showLoading = function () {
            var source = $("#access-loading").html(),
                template = Handlebars.compile(source);

            $content.html(template());
        },
        _displayOfficeAccessDelegatable = function (netids) {
            var source = $("#office_access_panel").html(),
                template = Handlebars.compile(source),
                context = {
                    access: [],
                    conflict: []
                },
                unique_netids = [],
                accessee_index = 0;

            $.each(netids, function(netid) {
                var name = this.name;

                if (this.conflict.length > 0) {
                    $.each(this.conflict, function(i, d) {
                        context.conflict.push({
                            mailbox: d.accessee.netid,
                            name: d.accessee.display_name,
                            delegate: d.accessor.name,
                            rights: d.rights,
                            accessee_index: accessee_index,
                            access_index: i
                        });
                    });
                }

                if (unique_netids.indexOf(netid) < 0) {
                    unique_netids.push(netid);
                }

                if (this.access.length > 0) {
                    $.each(this.access, function(i, d) {
                        var renewal_date = _renewalDate(d.datetime_granted);

                        context.access.push({
                            is_valid: true,
                            mailbox: d.accessee.netid,
                            name: d.accessee.display_name,
                            delegate: d.accessor.name,
                            date_granted: DateTime.utc2localdate(d.datetime_granted),
                            date_renewal: _renewalDateFormat(renewal_date),
                            date_renewal_relative: renewal_date.fromNow(),
                            right_id: d.access_right.name,
                            accessee_index: accessee_index,
                            access_index: i
                        });
                    });
                } else {
                    context.access.push({
                        is_valid: true,
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
            $('[data-toggle="popover"]').popover();
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
                var v = this,
                    mailbox = this.mailbox,
                    delegate = this.name,
                    $rows = $('.office-access-table tr[data-mailbox="' + v.mailbox + '"]');

                $rows.each(function (i) {
                    var $this_row = $(this),
                        row_delegate = $this_row.attr('data-delegate');
                    if (v.name == row_delegate) {
                        Notify.warning('Access for ' + row_delegate + ' already provided.');
                        return false;
                    } else if (v.name < row_delegate || i === $rows.length - 1) {
                        html = template({
                            new_delegate: true,
                            is_valid: v.is_valid,
                            message: v.message,
                            mailbox: v.mailbox,
                            name: $('td.access-mailbox-name', $this_row).text(),
                            delegate: v.name,
                            delegate_link: _getDelegateLink(v.name),
                            accessee_index: $this_row.hasClass('endorsee_row_even') ? 0 : 1,
                            access_index: i});

                        if (v.name < row_delegate) {
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
                            if (v.mailbox == $this_row.attr('data-mailbox')) {
                                $this_row.next('tr')
                                    .removeClass('endorsement_row_first top-border')
                                    .addClass('endorsement_row_following hidden-names');
                            }
                        }

                        _loadOfficeAccessTypeOptions(0, $('.access-type select',
                                                          _accessTableRow(v.mailbox, v.name)));
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
                action: "provision",
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
            });
        },
        _confirmNetidRevokeModal = function ($row) {
            var context = {
                action: "revoke",
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
            });
        },
        _confirmNetidRenewModal = function ($row) {
            var context = {
                action: "renew",
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
            });
        },
        _confirmNetidUpdateModal = function ($row) {
            var new_access_type = $('select.office-access-types option:selected', $row).val(),
                current_access_type = $('.access-type select').attr('data-access-right-id'),
                context = {
                    action: "update",
                    mailbox: $row.attr('data-mailbox'),
                    delegate: $row.attr('data-delegate'),
                    previous_access_type: current_access_type,
                    previous_access_type_name: _accessTypeName(current_access_type),
                    access_type: new_access_type,
                    access_type_name: _accessTypeName(new_access_type)
                };

            _displayModal("#confirm_update_modal_content", context);
            $panel.one('shown.bs.modal', '#access_netids_modal', function(e) {
                $('button#confirm_netid_update').one('click', function(e) {
                    $panel.trigger('endorse:OfficeDelegateUpdate', [context]);
                });
            });
        },
        _accessTypeName = function (type_id) {
            return $('.access-type select option[value="' + type_id + '"]', $content).first().text();
        },
        _grantedNetidAccessModal = function (context) {
            var template;

            if (context.action === 'renew') {
                template = '#renewed_netid_modal_content';
                context.renewal_date = _renewalDateFormat(moment().add(1, 'Y'));
            } else if (context.action === 'update') {
                template = "#updated_netid_modal_content";
            } else {
                template = "#granted_netid_modal_content";
            }

            if (!context.right_name) {
                context.right_name = _accessTypeName(context.right_id);
            }

            _displayModal(template, context);
        },
        _revokedNetidAccessModal = function (context) {
            _displayModal("#revoked_netid_modal_content", context);
        },
        _resolvedAccessModal = function (context) {
            _displayModal("#resolved_conflict_modal_content", context);
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
            $('body').removeClass('modal-open');
            $('.modal-backdrop').remove();
        },
        _updateOfficeAccessDisplay = function (context) {
            var $row = _accessTableRow(context.accessee.netid, context.accessor.name),
                source = $("#office_access_row_partial").html(),
                template = Handlebars.compile(source),
                delegate = (!context.is_revoke) ? context.accessor.name : null,
                renewal_date = _renewalDate(context.datetime_granted),
                html;

            html = template({
                is_valid: true,
                mailbox: context.accessee.netid,
                name: context.accessee.display_name,
                delegate: delegate,
                delegate_link: _getDelegateLink(delegate),
                date_granted: DateTime.utc2localdate(context.datetime_granted),
                date_renewal: _renewalDateFormat(renewal_date),
                date_renewal_relative: renewal_date.fromNow(),
                right_id: context.right_id,
                accessee_index: $row.hasClass('endorsee_row_even') ? 0 : 1,
                access_index: $row.hasClass('endorsement_row_first') ? 0 : 1});
            $row.replaceWith(html);
            $row = _accessTableRow(context.accessee.netid, context.accessor.name);
            _loadOfficeAccessTypeOptions(context.right_id,
                                         $('.office-access-types', $row));
        },
        _renewalDate = function (datetime) {

            return datetime ? moment(datetime).add(365, 'days') : moment();
        },
        _renewalDateFormat = function (mdatetime) {
            return (mdatetime) ? mdatetime.format('MM/DD/YYYY') : "";
        },
        _getDelegateLink = function (delegate) {
            return (delegate && delegate.match(/^u[w]?_.+/)) ?
                'https://groups.uw.edu/group/' + delegate : null;
        },
        _deleteOfficeAccessDisplay = function (context) {
            var selector = '.office-access-table tbody tr[data-mailbox="' + context.accessee.netid + '"]',
                mailbox_rows = -1,
                delete_row = -1,
                $delete_row;

            $(selector, $content).each(function () {
                var $row = $(this);

                mailbox_rows += 1;
                if ($row.attr('data-delegate') == context.accessor.name) {
                    delete_row = mailbox_rows;
                    $delete_row = $row;
                } else if ($delete_row) {
                    if (delete_row === 0) {
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
                if (mailbox_rows === 0) {
                    var source = $("#office_access_row_partial").html(),
                        template = Handlebars.compile(source),
                        html = template({
                            is_valid: true,
                            mailbox: context.accessee.netid,
                            name: context.accessee.display_name,
                            delegate: null,
                            accessee_index: $delete_row.hasClass('endorsee_row_even') ? 0 : 1,
                            access_index: 0});
                    $delete_row.replaceWith(html);
                } else {
                    $delete_row.remove();
                }
            }
        },
        _setAccessForDelegate = function (context) {
            _setDelegateAccess(context);
        },
        _updateAccessForDelegate = function (context) {
            _setDelegateAccess(context, 'PATCH');
        },
        _setDelegateAccess = function (context, method) {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

            $.ajax({
                url: "/office/v1/access",
                type: method ? method : "POST",
                data: JSON.stringify(context),
                contentType: "application/json",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    results.action = context.action;
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
                url: '/office/v1/access?mailbox=' + context.mailbox +
                    '&delegate=' + context.delegate +
                    '&access_type=' + context.access_type,
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
        _getNetidList = function () {
            var $textarea = $('.validate-netid-list textarea'),
                netids = $textarea.val(),
                netid_list = (netids) ? _unique(
                    netids.toLowerCase()
                        .replace(/\n/g, ' ')
                        .replace(/([a-z0-9]+)(@(uw|washington|u\.washington)\.edu)?/g, '$1')
                        .split(/[ ,]+/))
                        : [];

            if (netid_list.length) {
                var mailbox = $textarea.attr('data-mailbox'),
                    i = netid_list.indexOf(mailbox);

                if (i >= 0) {
                    netid_list.splice(i, 1);
                }
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
                    .text('-- Select access type --')
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
        _getOfficeAccessTypes = function($event_panel) {
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
                    window.access.office.types = results;
                    $event_panel.trigger('endorse:OfficeAccessTypesSuccess');
                },
                error: function(xhr, status, error) {
                    $event_panel.trigger('endorse:OfficeAccessTypesFailure', [error]);
                }
            });
        },
        _resolveAccessConflict = function (mailbox, delegate, right) {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

            $.ajax({
                url: "/office/v1/access/resolve",
                type: "POST",
                data: JSON.stringify({
                    mailbox: mailbox,
                    delegate: delegate,
                    access_type: right
                }),
                contentType: "application/json",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    $panel.trigger('endorse:OfficeAccessResolveSuccess', [results]);
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:OfficeAccessResolveFailure', [error]);
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
                $update_button = $('button#access_update', $buttons);

            if ($('option:first', $select).val().length === 0) {
                if ($('option:selected', $select).val() !== 0) {
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
        },
        _adjustTabLocation = function (tab) {
            History.addPath('access');
        },
        _showTab = function () {
            if (window.location.pathname.match(/\/access$/)) {
                setTimeout(function(){
                    $('.tabs .tabs-list li[data-tab="access"] span').click();
                },100);
            }
        };

    return {
        load: function () {
            _registerEvents();
            _showTab();
        },
        getOfficeAccessTypes: _getOfficeAccessTypes
    };
}());

export { ManageOfficeAccess };
