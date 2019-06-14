// common service endorsement renewal javascript

var Renew = {
    load: function () {
        this._loadContainer();
        this._registerEvents();
    },

    _loadContainer: function () {
        $('#app_content').append($("#renew_modal_container").html());
    },

    _registerEvents: function () {
        $(document).on('click', 'button#confirm_renew_responsibility', function (e) {
            var $button = $(this),
                to_renew;

            to_renew = Endorse._gatherEndorsementsByRow($button.data('$rows'), 'renew', true, true);
            Renew._renewUWNetID(to_renew, $button.data('$panel'));
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

    renew: function ($rows) {
        var $modal = $('#renew_modal'),
            template = Handlebars.compile($('#renew_modal_content').html()),
            context = Renew._renewModalContext($rows);

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
        $modal.find('button#confirm_renew_responsibility')
            .data('$rows', $rows)
            .data('$panel', $rows.closest('div.panel'));
    },

    _successModal: function (renewed) {
        var source = $("#renew_success_modal_content").html(),
            template = Handlebars.compile(source),
            $modal = $('#renew_success_modal'),
            context = {
                renewal_date: moment().add(1, 'Y').format('MM/DD/YYYY'),
                unique: [],
                renew_o365: [],
                renew_google: [],
                renew_netid_count: 0
            };

        $.each(renewed, function (netid, services) {
            if (context.unique.indexOf(netid) < 0) {
                context.unique.push(netid);
            }

            if (services.endorsements.hasOwnProperty('o365')) {
                context.renew_o365.push({
                    netid: netid
                });
            }

            if (services.endorsements.hasOwnProperty('google')) {
                context.renew_google.push({
                    netid: netid
                });
            }
        });

        $('.modal-content', $modal).html(template(context));
        $modal.modal('show');
    },

    _renewModalContext: function ($rows) {
        var renew_o365 = [],
            renew_google = [],
            context = {
                renewer: window.user.netid,
                unique: [],
                renew_o365: [],
                renew_google: [],
                renew_netid_count: 0,
                renew_o365_netid_count: 0,
                renew_google_netid_count: 0
            };

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

            if (service === 'o365') {
                context.renew_o365.push({
                    netid: netid,
                    email: email
                });
            }

            if (service === 'google') {
                context.renew_google.push({
                    netid: netid,
                    email: email
                });
            }
        });

        return context;
    },

    _renewUWNetID: function(renewees, $panel) {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $(document).trigger('endorse:UWNetIDsRenewStart', [renewees]);

        $.ajax({
            url: "/api/v1/endorse/",
            dataType: "JSON",
            data: JSON.stringify(renewees),
            type: "POST",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {

                // pause for renew modal fade
                if (results.endorsed) {
                    setTimeout(function () {
                        Renew._successModal(results.endorsed);
                    }, 500);
                }

                $panel.trigger('endorse:UWNetIDsRenewSuccess', [{
                    renewees: renewees,
                    renewed: results
                }]);
            },
            error: function(xhr, status, error) {
                $panel.trigger('endorse:UWNetIDsRenewError', [error]);
            }
        });
    }
};
