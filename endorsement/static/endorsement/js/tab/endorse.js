// javascript for service endorsement provisioning

var ProvisionServices = {
    hash: '#provision',

    load: function () {
        this._loadTab();
        this._registerEvents();
        this._enableCheckEligibility();
    },

    focus: function () {
        if (window.location.hash === this.hash) {
            $('a[href="' + this.hash + '"]').tab('show');
            $('#netid_list:visible').focus();
        }
    },

    _loadTab: function () {
        var tab_link = $("#provision-tab-link").html(),
            tab_content = $("#provision-tab-content").html();
        
        $('.nav-tabs').append(tab_link);
        $('.tab-content').append(tab_content);
    },

    _registerEvents: function () {
        $('#app_content').on('click', 'button#validate', function(e) {
            var $this = $(this);

            $this.button('loading');
            ProvisionServices._validateUWNetids(ProvisionServices._getNetidList());
        }).on('input', '#netid_list', function () {
            ProvisionServices._enableCheckEligibility();
        }).on('change', '#netid_list',  function(e) {
            ProvisionServices._enableCheckEligibility();
        }).on('click', 'button#netid_input', function(e) {
            ProvisionServices._showInputStep();
        }).on('change', 'input[name^="endorse_"]', function (e) {
            ProvisionServices._enableEndorsability();
        }).on('change', '#accept_responsibility',  function(e) {
            if (this.checked) {
                $('button#endorse').removeAttr('disabled');
            } else {
                $('button#endorse').attr('disabled', 'disabled');
            }
        }).on('click', 'button#new_netid_input', function(e) {
            $('#netid_list').val('');
            $('.endorsement-group input:checked').prop('checked', false);
            ProvisionServices._enableCheckEligibility();
            ProvisionServices._showInputStep();
        }).on('click', '.edit-email', function (e) {
            var $row = $(e.target).closest('tr'),
                $editor = $('.email-editor', $row);

            if ($row.hasClass('unchecked')) {
                return false;
            }

            $('.displaying-email', $row).addClass('visually-hidden');
            $('.editing-email', $row).removeClass('visually-hidden');
            $editor.val($('.shown-email', $row).html());
            $editor.focus();
        }).on('click', '.finish-edit-email', function (e) {
            var $row = $(e.target).closest('tr');

            ProvisionServices._finishEmailEdit($('.email-editor', $row));
        }).on('focusout', '.email-editor', function(e) {
            ProvisionServices._finishEmailEdit($(e.target));
        }).on('click', 'button#endorse', function(e) {
            var $this = $(this);

            $this.parents('.modal').modal('hide');
            $('#confirm_endorsements').button('loading').addClass('loading');
            ProvisionServices._endorseUWNetIDs(ProvisionServices._getEndorseNetids());
        }).on('keypress', function (e) {
            if ($(e.target).hasClass('email-editor') && e.which == 13) {
                ProvisionServices._finishEmailEdit($(e.target));
            }
        });

        $(document).on('shown.bs.tab', 'a[href="#provision"]', function (e) {
            $('#netid_list:visible').focus();
        }).on('endorse:UWNetIDsValidated', function (e, validated) {
            $('button#validate').button('reset');
            ProvisionServices._displayValidatedUWNetIDs(validated);
        }).on('endorse:UWNetIDReasonEdited', function (e, validated) {
            ProvisionServices._enableEndorsability();
        }).on('endorse:UWNetIDsInvalidEmailError', function (e, $row, $td) {
            if ($('input[type="checkbox"]:checked', $row).length > 0) {
                $td.addClass('error');
            }
        }).on('endorse:UWNetIDsInvalidReasonError', function (e, $row, $td) {
            if ($('input[type="checkbox"]:checked', $row).length > 0) {
                $td.addClass('error');
                $('button#shared_update').attr('disabled', 'disabled');
            }
        }).on('endorse:UWNetIDChangedReason', function (e) {
            ProvisionServices._enableEndorsability();
        }).on('endorse:UWNetIDApplyAllReasons', function (e) {
            ProvisionServices._enableEndorsability();
        }).on('endorse:UWNetIDsEndorseStatus', function (e, endorsed) {
            $('button#confirm_endorsements').button('reset');
            ProvisionServices._displayEndorseResult(endorsed);
        }).on('show.bs.modal', '#responsibility_modal' ,function (event) {
            var _modal = $(this);

            _modal.find('input#accept_responsibility').attr('checked', false);
            _modal.find('button#endorse').attr('disabled', 'disabled');
        });
    },

    _enableEndorsability: function() {
        var $netids = $('.endorsed_netid'),
            endorsable = $netids.length > 0,
            unchecked = 0,
            $button = $('button#confirm_endorsements');

        $('div#uwnetids-validated td.error').removeClass('error');
        $netids.each(function () {
            var $row = $(this).closest('tr'),
                $email = $('.shown-email', $row),
                $td = $email.closest('td'),
                reason = Reasons.getReason($row);

            if ($('input[type="checkbox"]:checked', $row).length > 0) {
                $row.removeClass('unchecked');
                $(".email-editor", $row).removeAttr('disabled');
                if (!ProvisionServices._validEmailAddress($email.html(), $row, $td) ||
                    reason.length <= 0) {
                    endorsable = false;
                }
            } else {
                unchecked += 1;
                $row.addClass('unchecked');
                $(".email-editor", $row).attr('disabled', 'disabled');
            }
        });

        if (endorsable && unchecked < $netids.length) {
            $button.removeAttr('disabled');
        } else {
            $button.attr('disabled', 'disabled');
        }

        if (unchecked == $netids.length) {
            $button.addClass('no_netids');
        } else {
            $button.removeClass('no_netids');
        }
    },

    _displayValidatedUWNetIDs: function(validated) {
        var source = $("#validated-list").html();
        var template = Handlebars.compile(source);
        var $endorsement_group = $('.endorsement-group input[type="checkbox"]');
        var context = {
            netids: validated.validated,
            netid_count: validated.validated.length
        };

        $.each(context.netids, function () {
            this.valid_netid = (this.error === undefined);

            if (this.google && this.google.error === undefined) {
                context.google_endorsable = true;
                this.google.eligible = true;
            }
            if (this.o365 && this.o365.error === undefined) {
                context.o365_endorsable = true;
                this.o365.eligible = true;
            }
        });

        $('#uwnetids-validated').html(template(context));

        $endorsement_group.attr('disabled', true);
        ProvisionServices._showValidationStep();
        ProvisionServices._enableEndorsability();

        $('.email-editor').each(function() {
            ProvisionServices._finishEmailEdit($(this));
        });
    },

    _displayEndorseResult: function(endorsed) {
        var source = $("#endorse-result").html();
        var template = Handlebars.compile(source);
        var context = {
            can_revoke: false,
            has_endorsed: (endorsed && Object.keys(endorsed.endorsed).length > 0),
            endorsed: endorsed
        };

        $('#uwnetids-endorsed').html(template(context));
        ProvisionServices._showEndorsedStep();
    },

    _finishEmailEdit: function($editor) {
        var email = $.trim($editor.val()),
            $td = $editor.closest('td'),
            $row = $td.closest('tr'),
            netid = $('.endorsed_netid', $row).html(),
            name = $('.endorsed_name', $row).html();

        // update shown email
        $('.shown-email', $row).html(email);

        if (email.length &&
            ProvisionServices._validEmailAddress(email, $row, $td)) {
            // hide editor
            $('.editing-email', $row).addClass('visually-hidden');
            $('.displaying-email', $row).removeClass('visually-hidden');

            // update success indicator
            $('.finish-edit-email', $row).find('>:first-child')
                .removeClass("fa-minus-circle failure")
                .addClass('fa-check success');
        } else {
            // show editor
            $('.editing-email', $row).removeClass('visually-hidden');
            $('.displaying-email', $row).addClass('visually-hidden');

            // update success indicator
            $('.finish-edit-email', $row).find('>:first-child')
                .addClass("fa-minus-circle failure")
                .removeClass('fa-check success');
        }

        ProvisionServices._enableEndorsability();
    },

    _validEmailAddress: function(email_address, $row, $td) {
        var pattern = /^([a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+(\.[a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)*|"((([ \t]*\r\n)?[ \t]+)?([\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*(([ \t]*\r\n)?[ \t]+)?")@(([a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.)+([a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.?$/i,
            result = pattern.test(email_address);
        if (!result) {
            $(document).trigger('endorse:UWNetIDsInvalidEmailError', [$row, $td]);
        }

        return result;
    },

    _enableCheckEligibility: function() {
        var netids = ProvisionServices._getNetidList();

        if (netids.length > 0) {
            $('#validate').removeAttr('disabled');
        } else {
            $('#validate').attr('disabled', 'disabled');
        }
    },

    _getNetidList: function () {
        var netid_list = $('#netid_list').val().toLowerCase();
        if (netid_list) {
            return ProvisionServices._unique(netid_list
                                .replace(/\n/g, ' ')
                                .replace(/([a-z0-9]+)(@(uw|washington|u\.washington)\.edu)?/g, '$1')
                                .split(/[ ,]+/));
        }

        return [];
    },

    _unique: function(array) {
        return $.grep(array, function(el, i) {
            return el.length > 0 && i === $.inArray(el, array);
        });
    },

    _getEndorseNetids: function () {
        var to_endorse = {};
        var validated = [];

        $('input[name="endorse_o365"]:checked').each(function (e) {
            var netid = $(this).val(),
                $row = $(this).closest('tr'),
                email = $('.shown-email', $row).html(),
                reason = Reasons.getReason($row);

            $.each(window.endorsement.validation.validated, function () {
                if (netid == this.netid) {
                    if (this.o365 && this.o365.eligible) {
                        if (netid in to_endorse) {
                            to_endorse[this.netid].o365 = true;
                            to_endorse[this.netid].email = email;
                            to_endorse[this.netid].reason = reason;
                        } else {
                            to_endorse[this.netid] = {
                                o365: true,
                                email: email,
                                reason: reason
                            };
                        }
                    }

                    return false;
                }
            });
        });

        $('input[name="endorse_google"]:checked').each(function (e) {
            var netid = $(this).val(),
                $row = $(this).closest('tr'),
                email = $('.shown-email', $row).html(),
                reason = Reasons.getReason($row);

            $.each(window.endorsement.validation.validated, function () {
                if (netid == this.netid) {
                    if (this.google && this.google.eligible) {
                        if (netid in to_endorse) {
                            to_endorse[this.netid].google = true;
                            to_endorse[this.netid].email = email;
                            to_endorse[this.netid].reason = reason;
                        } else {
                            to_endorse[this.netid] = {
                                google: true,
                                email: email,
                                reason: reason
                            };
                        }
                    }

                    return false;
                }
            });
        });

        return to_endorse;
    },

    _validateUWNetids: function(netids) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $.ajax({
            url: "/api/v1/validate/",
            dataType: "JSON",
            data: JSON.stringify(netids),
            type: "POST",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                window.endorsement = { validation: results };
                $(document).trigger('endorse:UWNetIDsValidated', [results]);
            },
            error: function(xhr, status, error) {
            }
        });
    },

    _endorseUWNetIDs: function(endorsees) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;
        var endorsed = {};

        $.each(window.endorsement.validation.validated, function () {
            var endorsement = endorsees[this.netid];

            if (endorsement !== undefined) {
                endorsed[this.netid] = {
                    'name': this.name,
                    'email': endorsement.email,
                    'reason': endorsement.reason
                };

                if (endorsement.o365 !== undefined) {
                    endorsed[this.netid].o365 = endorsement.o365;
                }

                if (endorsement.google !== undefined) {
                    endorsed[this.netid].google = endorsement.google;
                }
            }
        });

        $.ajax({
            url: "/api/v1/endorse/",
            dataType: "JSON",
            data: JSON.stringify(endorsed),
            type: "POST",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                $(document).trigger('endorse:UWNetIDsEndorseStatus', [results]);
            },
            error: function(xhr, status, error) {
            }
        });
    },

    _showInputStep: function () {
        $('.endorsement-group input').removeAttr('disabled');
        $('#uwnetids-validated').hide();
        $('#uwnetids-endorsed').hide();
        $('#uwnetids-input').show();
    },

    _showValidationStep: function () {
        $('.endorsement-group input').attr('disabled', true);
        $('#uwnetids-input').hide();
        $('#uwnetids-endorsed').hide();
        $('#uwnetids-validated').show();
    },

    _showEndorsedStep: function () {
        $('.endorsement-group input').attr('disabled', true);
        $('#uwnetids-input').hide();
        $('#uwnetids-validated').hide();
        $('#uwnetids-endorsed').show();
    }

}
