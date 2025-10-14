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
            }).on('click', '#validate_netids_access', function (e) {
                var mailbox = $('.validate-netid-list textarea').attr('data-mailbox'),
                    delegates = _getNetidList();

                Button.loading($('#' + this.id, $content));
                _validateOfficeAccessUWNetIDs(mailbox, delegates);
            }).on('click', '#select_access_type', function (e) {
                var $action = $(this),
                    $row = $action.closest('tr');

                _selectNetidAccessModal($row);
            }).on('click', '#access_update', function (e) {
                var $action = $(this),
                    $row = $action.closest('tr');

                _selectNetidAccessModal($row);
            }).on('click', '#access_revoke', function (e) {
                var $button = $(this),
                    $row = $button.closest('tr');

                _confirmNetidRevokeModal($row);
            }).on('click', '#access_renew', function (e) {
                var $button = $(this),
                    $row = $button.closest('tr');

                _confirmNetidRenewModal($row);
            }).on('click', 'input.access-conflict', function (e) {
                var $this = $(this),
                    $button = $this.closest('td').find('button#access_resolve');

                $button.prop('disabled', false);
            }).on('click', 'button#access_resolve', function (e) {
                var $this = $(this),
                    $checked = $this.closest('td').find('input.access-conflict:checked'),
                    mailbox = $this.attr('data-mailbox'),
                    delegate = $this.attr('data-delegate'),
                    right = $checked.val();

                _resolveAccessConflict(mailbox, delegate,right);
            }).on('click', 'button#confirm_resolved_conflict', function (e) {
                _modalHide();
                $('.tabs div#access').trigger('endorse:accessTabExposed');
            }).on('click', 'a#toggle_permission_details', function (e) {
                $('.access-types-explained').toggle();
                $(this).find('span').text($('.access-types-explained').is(':visible') ? 'Hide' : 'Show');
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
                _modalHide();
                _updateOfficeAccessDisplay(context);
                _grantedNetidAccessModal(context);
            }).on('endorse:OfficeDelegateAccessFailure', function (e, accessee, error) {
                var $row = _accessTableRow(accessee.mailbox, accessee.delegate);

                _modalHide();
                _access_error_notification('Access error' + ((error && error.length) ? ': ' + error : '.'));
            }).on('endorse:OfficeDelegateRevokeSuccess', function (e, context) {
                _modalHide();
                _deleteOfficeAccessDisplay(context);
                _revokedNetidAccessModal(context);
            }).on('endorse:OfficeDelegateRevokeFailure', function (e, context, error) {
                var $row = _accessTableRow(context.mailbox, context.name);

                _modalHide();
                _access_error_notification('Revoke error' + ((error && error.length) ? ': ' + error : '.'));
            }).on('endorse:OfficeAccessResolveSuccess', function (e, data) {
                _resolvedAccessModal(data);
            }).on('endorse:OfficeAccessResolveFailure', function (e, data) {
                _access_error_notification('Resolve error' + ((data && data.length) ? ': ' + data : '.'));
            }).on('endorse:OfficeAccessTypesSuccess', function (e) {
                _displayOfficeAccessTypes();
            }).on('endorse:OfficeAccessTypesFailure', function (e, data) {
                alert('Cannot determine Access Types: ' + data);
            }).popover({
                selector: 'span.prt-data-popover',
                trigger: 'focus',
                html: true
            });

            $(document).on('endorse:TabChange', function (e, data) {
                if (data == 'access') {
                    _adjustTabLocation();
                }
            }).on('change', '#access_netids_modal select', function () {
                var $modal = $(this).closest('#access_netids_modal'),
                    $selected = $('option:selected', this),
                    $select_button = $('button#select_netid_access', $modal);

                if ($selected.val()) {
                    $select_button.removeAttr('disabled');
                } else {
                    $select_button.attr('disabled', 'disabled');
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
                            delegate_link: _getDelegateLink(d.accessor.name),
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
                            delegate_link: _getDelegateLink(d.accessor.name),
                            date_granted: DateTime.utc2localdate(d.datetime_granted),
                            date_renewal: _renewalDateFormat(renewal_date),
                            date_renewal_relative: renewal_date.fromNow(),
                            right_name: d.access_right.display_name,
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
                    $panel.trigger('endorse:OfficeDelegatableFailure', [_error_message(xhr)]);
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
                    $panel.trigger('endorse:OfficeValidateNetIDsFailure', [_error_message(xhr)]);
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

                if ($('tr[data-mailbox="' + mailbox  + '"][data-delegate="' + delegate + '"]').length > 0) {
                    Notify.warning('Access for ' + delegate + ' already provided.', 10000);
                    return true;
                }

                $rows.each(function (i) {
                    var $this_row = $(this),
                        row_delegate = $this_row.attr('data-delegate');

                    if (v.name < row_delegate || i === $rows.length - 1) {
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
        _selectNetidAccessModal = function ($row) {
            var $access_select,
                right_id = $row.attr('data-right-id'),
                context = {
                    mailbox: $row.attr('data-mailbox'),
                    delegate: $row.attr('data-delegate'),
                    access_type: right_id,
                    access_type_name: _accessTypeName(right_id)
                };

            _displayModal("#select_access_modal_content", context);

            $panel.one('shown.bs.modal', '#access_netids_modal', function(e) {
                var $access_select = $('#access_netids_modal .modal-body .office-access-types');

                _loadOfficeAccessTypeOptions(context.access_type, $access_select);

                $('button#select_netid_access').one('click', function(e) {
                    var new_access_type = $('option:selected', $access_select).val(),
                        new_access_type_name = $('option:selected', $access_select).text();

                    $panel.one('hidden.bs.modal', '#access_netids_modal', function(e) {
                        if (context.access_type) {
                            if (context.access_type !== new_access_type) {
                                context.action = "update";
                                context.previous_access_type = context.access_type;
                                context.previous_access_type_name = context.access_type_name;
                                context.access_type = new_access_type;
                                context.access_type_name = new_access_type_name;
                                context.access_type = new_access_type;
                                context.access_type_name = new_access_type_name;

                                _displayModal("#confirm_update_modal_content", context);
                                $panel.one('shown.bs.modal', '#access_netids_modal', function(e) {
                                    $('button#confirm_netid_update').one('click', function(e) {
                                        var $button = $(this),
                                            $row = _accessTableRow(context.mailbox, context.delegate);

                                        Button.loading($button);
                                        _modalDisable();
                                        _updateAccessForDelegate(context);
                                    });
                                });
                            }
                        } else {
                            context.access_type = new_access_type;
                            context.access_type_name = new_access_type_name;
                            _confirmNetidAccessModal(context);
                        }
                    });

                    _modalHide();
                });
            });
        },
        _confirmNetidAccessModal = function (context) {
            context.action = "provision";

            _displayModal("#confirm_netids_modal_content", context);
            $panel.one('shown.bs.modal', '#access_netids_modal', function(e) {
                $('button#confirm_netid_access').one('click', function(e) {
                    var $button = $(this),
                        $row = _accessTableRow(context.mailbox, context.delegate);

                    Button.loading($button);
                    _modalDisable();
                    _setAccessForDelegate(context);
                });
            });
        },
        _confirmNetidRevokeModal = function ($row) {
            var right_id = $row.attr('data-right-id'),
                context = {
                    action: "revoke",
                    mailbox: $row.attr('data-mailbox'),
                    delegate: $row.attr('data-delegate'),
                    access_type: right_id,
                    access_type_name: _accessTypeName(right_id)
                };

            _displayModal("#confirm_revoke_modal_content", context);
            $panel.one('shown.bs.modal', '#access_netids_modal', function(e) {
                $('button#confirm_netid_revoke').one('click', function(e) {
                    var $button = $(this),
                        $row = _accessTableRow(context.mailbox, context.delegate);

                    Button.loading($button);
                    _modalDisable();
                    _revokeAccessForDelegate(context);
                });
            });
        },
        _confirmNetidRenewModal = function ($row) {
            var context = {
                action: "renew",
                mailbox: $row.attr('data-mailbox'),
                delegate: $row.attr('data-delegate')
            };

            _displayModal("#confirm_renew_modal_content", context);
            $panel.one('shown.bs.modal', '#access_netids_modal', function(e) {
                $('button#confirm_netid_renew').one('click', function(e) {
                    var $button = $(this),
                        $row = _accessTableRow(context.mailbox, context.delegate);

                    Button.loading($button);
                    _modalDisable();
                    _updateAccessForDelegate(context);
                });
            });
        },
/*        _confirmNetidUpdateModal = function ($row) {
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
*/
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
            var $modal = $('#access_netids_modal', $content);

            $modal.modal('show');
            $modal.data('bs.modal')._config.keyboard = true;
            $modal.data('bs.modal')._config.backdrop = undefined;
        },
        _modalHide = function () {
            $('#access_netids_modal', $content).modal('hide');
            $('body').removeClass('modal-open');
            $('.modal-backdrop').remove();
        },
        _modalDisable = function () {
            var $modal = $('#access_netids_modal', $content);

            $modal.find("button[data-dismiss]").attr('disabled', 'disabled');

            $modal.data('bs.modal')._config.keyboard = false;
            $modal.data('bs.modal')._config.backdrop = 'static';
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
                right_id: context.access_right.name,
                right_name: context.access_right.display_name,
                accessee_index: $row.hasClass('endorsee_row_even') ? 0 : 1,
                access_index: $row.hasClass('endorsement_row_first') ? 0 : 1});
            $row.replaceWith(html);
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
                    $panel.trigger('endorse:OfficeDelegateAccessFailure', [context, _error_message(xhr)]);
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
                    $panel.trigger('endorse:OfficeDelegateRevokeFailure', [context, _error_message(xhr)]);
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
                    $event_panel.trigger('endorse:OfficeAccessTypesFailure', [_error_message(xhr)]);
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
                    $panel.trigger('endorse:OfficeAccessResolveFailure', [_error_message(xhr)]);
                }
            });

        },
        _error_message = function (xhr) {
            var xhr_content_type = xhr.getResponseHeader('content-type');

            if (xhr_content_type === 'application/json') {
                if (xhr.responseJSON.hasOwnProperty('error')) {
                    var error = xhr.responseJSON.error;

                    if (typeof(error) === 'string') {
                        return error;
                    } else if (typeof(error) === 'object') {
                        if (error.hasOwnProperty('error')) {
                            return error.error;
                        } else if (error.hasOwnProperty('msg')) {
                            return error.msg;
                        }
                    }
                }
            }

            return xhr.statusText || "";
        },
        _access_error_notification = function (message) {
            Notify.error(message + '&nbsp; Please try again later.', 15000);
        },
        _scrollNetIDIntoView = function (netid) {
            Scroll.scrollToNetid(netid, '.office-access-table');
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
