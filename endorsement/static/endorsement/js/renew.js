// common service endorsement renewal javascript
/* jshint esversion: 6 */

import { Endorse } from "./endorse.js";

var Renew = (function () {
    var _loadContainer = function () {
        $('#app_content').append($("#renew_modal_container").html());
    },

    _registerEvents = function () {
        $(document).on('click', 'button#confirm_renew_responsibility', function (e) {
            var $button = $(this),
                to_renew;

            to_renew = Endorse.gatherEndorsementsByRow($button.data('$rows'), 'renew', true, true);
            _renewUWNetID(to_renew, $button.data('$panel'));
            $button.closest('.modal').modal('hide');
        }).on('change', '#renew_modal input', function () {
            var $modal = $(this).closest('#renew_modal'),
                $accept_button = $('button#confirm_renew_responsibility', $modal),
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
        });
    },

    _successModal = function (renewed) {
        var source = $("#renew_success_modal_content").html(),
            template = Handlebars.compile(source),
            $modal = $('#renew_success_modal'),
            context = {
                renewal_date: moment().add(1, 'Y').format('MM/DD/YYYY'),
                unique: [],
                services: {}
            };

        $.each(window.endorsed_services, function(k, v) {
            context.services[k] = {
                'renew': []
            };
        });

        $.each(renewed, function (netid, services) {
            if (context.unique.indexOf(netid) < 0) {
                context.unique.push(netid);
            }

            $.each(window.endorsed_services, function(k, v) {
                $.each(services, function(s) {
                    if (services.endorsements.hasOwnProperty(k)) {
                        context.services[k].renew.push({
                            netid: netid
                        });
                    }
                });
            });
        });

        context.netid_count = context.unique.length;

        $.each(context.services, function(k) {
            context.services[k].count = context.services[k].renew.length;
        });

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
    },

    _renewModalContext = function ($rows) {
        var context = {
                renewer: window.user.netid,
                unique: [],
                services: {}
            };

        $.each(window.endorsed_services, function(k, v) {
            context.services[k] = {
                'name': v.category_name,
                'renew': []
            };
        });

        $rows.each(function (i, row) {
            var $row = $(row),
                netid = $row.attr('data-netid'),
                netid_name = $row.attr('data-netid-name'),
                email = $row.attr('data-netid-initial-email'),
                service = $row.attr('data-service'),
                service_name = $row.attr('data-service-name');

            if (context.unique.indexOf(netid) < 0) {
                context.unique.push(netid);
            }

            if (context.services.hasOwnProperty(service)) {
                context.services[service].renew.push({
                    netid: netid,
                    email: email
                });
            }
        });

        context.netid_count = context.unique.length;

        $.each(context.services, function(k) {
            context.services[k].count = context.services[k].renew.length;
        });

        return context;
    },

    _renewUWNetID = function(renewees, $panel) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $(document).trigger('endorse:UWNetIDsRenewStart', [renewees]);

        $.ajax({
            url: "/api/v1/endorse/",
            type: "POST",
            data: JSON.stringify({'endorsees': renewees }),
            contentType: "application/json",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {

                // pause for renew modal fade
                if (results.endorsed) {
                    setTimeout(function () {
                        _successModal(results.endorsed);
                    }, 500);
                }

                $panel.trigger('endorse:UWNetIDsRenewSuccess', [{
                    renewees: renewees,
                    renewed: results
                }]);
            },
            error: function(xhr, status, error) {
                $panel.trigger('endorse:UWNetIDsRenewError', [renewees, error]);
            }
        });
    };

    return {
        load: function () {
            _loadContainer();
            _registerEvents();
        },
        renew: function ($rows) {
            var $modal = $('#renew_modal'),
                template = Handlebars.compile($('#renew_modal_content').html()),
                context = _renewModalContext($rows);

            $('.modal-content', $modal).html(template(context));
            $modal.modal('show');
            $modal.find('button#confirm_renew_responsibility')
                .data('$rows', $rows)
                .data('$panel', $rows.closest('div.netid-panel'));
        },
        resetRenewButton: function (renewees) {
            Endorse.resetActionButton('renew', renewees);
        }
    };
}());

export { Renew };
