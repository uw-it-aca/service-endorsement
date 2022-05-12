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

                _modalButtonLoading('#' + this.id);
                _validateOfficeAccessUWNetIDs(mailbox, delegates);
            }).on('click', '#provision_access', function (e) {
                var $button = $(this),
                    $row = $button.closest('tr');

                _confirmNetidAccessModal($row);
            }).on('endorse:OfficeDelegateConfirmation', function (e, context) {
                _hideModal();
                _modalButtonLoading('#provision_access', context.mailbox, context.delegate)
                _setAccessForDelegate(context);
            }).on('endorse:OfficeDelegatableSuccess', function (e, data) {
                _displayOfficeAccessUWNetIDs(data.netids);
                _getOfficeAccessTypes();
            }).on('endorse:OfficeDelegatableFailure', function (e, data) {
                _displayOfficeAccessUWNetIDFailure(data);
            }).on('endorse:OfficeValidateNetIDsSuccess', function (e, data) {
                _hideModal();
                _displayValidatedUWNetIDs(data);
            }).on('endorse:OfficeValidateNetIDsFailure', function (e, data) {
                _hideModal();
                _displayValidateNetIDsFailure(data);
            }).on('endorse:OfficeDelegateAccessSuccess', function (e, accessee) {
                _updateOfficeAccessDisplay(accessee);
            }).on('endorse:OfficeDelegateAccessFailure', function (e, accessee, error) {
                var $row = _accessTableRow(accessee.mailbox, accessee.name);

                Notify.error('Access error: ' + error);
                _modalButtonReset('#provision_access', accessee.mailbox, accessee.delegate);
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
        _displayModal = function (template_id, context) {
            var source = $(template_id).html(),
                template = Handlebars.compile(source);

            $('#access_netids_modal .modal-content', $content).html(template(context));
            _showModal();
        },
        _showModal = function () {
            $('#access_netids_modal', $content).modal('show');
        },
        _hideModal = function () {
            $('#access_netids_modal', $content).modal('hide');
        },
        _modalButtonLoading = function (id, netid, delegate) {
            Button.loading($(id, netid ? _accessTableRow(netid, delegate) : $content));
        },
        _modalButtonReset = function (id, netid, delegate) {
            Button.reset($(id, netid ? _accessTableRow(netid, delegate) : $content));
        },
        _updateOfficeAccessDisplay = function (accessee) {
            var $row = _accessTableRow(accessee.mailbox, accessee.delegate),
                source = $("#office_access_row_partial").html(),
                template = Handlebars.compile(source),
                html;

            if (!$row.length) {
                return;
            }

            html = template({
                mailbox: accessee.mailbox,
                name: $('td.access-mailbox-name', $row).text(),
                delegate: accessee.delegate,
                status: 'Provisioned',
                accessee_index: $row.hasClass('endorsee_row_even') ? 0 : 1,
                access_index: $row.parent().children().index($row)});
            $row.replaceWith(html);
            $row = _accessTableRow(accessee.mailbox, accessee.delegate);
            _loadOfficeAccessTypeOptions(accessee.right_id,
                                         $('.office-access-types', $row));
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
                    $panel.trigger('endorse:OfficeDelegateAccessFailure', [accessee, error]);
                }
            });
        },
        _revokeAccessForDelegate = function (netid, delegate, access_type) {
            var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

                accessee = {
                    "delegate": delegate,
                    "access_type": access_type
                };

            $.ajax({
                url: "/office/v1/access",
                type: "DELETE",
                data: JSON.stringify(accessee),
                contentType: "application/json",
                accepts: {html: "application/json"},
                headers: {
                    "X-CSRFToken": csrf_token
                },
                success: function(results) {
                    $panel.trigger('endorse:OfficeDelegateDeleteSuccess', [results]);
                },
                error: function(xhr, status, error) {
                    $panel.trigger('endorse:OfficeDelegateDeleteFailure', [accessee, error]);
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
            var $buttons = $select.closest('td').next('td'),
                $action_button = $('button[data-action]', $buttons),
                button_action = $action_button.attr('data-action'),
                button_action = $action_button.attr('data-action'),
                $revoke_button = $('button#access_revoke', $buttons),
                right_id = $select.attr('data-access-right-id');

            if (new_right_id) {
                $buttons.find('button').prop('disabled', false);
                if (button_action != 'provision') {
                    if (new_right_id == right_id) {
                        $action_button.text('Renew');
                        $action_button.attr('data-action', 'renew');
                    } else {
                        $action_button.text('Update');
                        $action_button.attr('data-action', 'update');
                        $revoke_button.prop('disabled', true);
                    }
                }
            } else {
                $buttons.find('button').prop('disabled', true);
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
