// javascript to Manage Provision Services

var ManageProvisionedServices = {
    hash: '#provisioned',

    load: function () {
        this._loadTab();
        this._registerEvents();
    },

    focus: function () {
        if (window.location.hash === this.hash) {
            $('a[href="' + this.hash + '"]').tab('show');
        }
    },

    _loadTab: function () {
        var tab_link = $("#provisioned-tab-link").html(),
            tab_content = $("#provisioned-tab-content").html();
        
        $('.nav-tabs').append(tab_link);
        $('.tab-content').append(tab_content);
    },

    _registerEvents: function () {
        $(ManageProvisionedServices.hash).on('click', 'button.confirm_revoke', function(e) {
            Revoke.revoke($(this), '#revoke_modal_content',
                          'endorse:UWNetIDsRevokeStatus');
        });

        $(document).on('shown.bs.tab', 'a[href="#provisioned"]', function (e) {
            ManageProvisionedServices._getEndorsedUWNetIDs();
        }).on('endorse:UWNetIDsEndorsed', function (e, endorsed) {
            $('button#confirm_endorsements').button('reset');
            ManageProvisionedServices._displayEndorsedUWNetIDs(endorsed);
        }).on('endorse:UWNetIDsRevokeStatus', function (e, data) {
            $.each(data.revokees, function (netid, endorsements) {
                $.each(endorsements, function (endorsement, state) {
                    var id = endorsement + '-' + netid;

                    $('.reason-' + id).html('');
                    $('.revoke-' + id).html('');
                    $('.endorsed-' + id).html($("#unendorsed").html());
                });
            });
        });
    },

    _getEndorsedUWNetIDs: function() {
        var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

        $('#provisioned').html($('#endorsed-loading').html());

        $.ajax({
            url: "/api/v1/endorsed/",
            dataType: "JSON",
            type: "GET",
            accepts: {html: "application/json"},
            headers: {
                "X-CSRFToken": csrf_token
            },
            success: function(results) {
                $(document).trigger('endorse:UWNetIDsEndorsed', [results]);
            },
            error: function(xhr, status, error) {
                $('#provisioned').html($('#endorsed-failure').html());
            }
        });
    },

    _displayEndorsedUWNetIDs: function(endorsed) {
        var source = $("#endorsed-netids").html();
        var template = Handlebars.compile(source);
        var context = {
            can_revoke: true,
            has_endorsed: (endorsed && Object.keys(endorsed.endorsed).length > 0),
            endorsed: endorsed
        };

        $('div.tab-pane#provisioned').html(template(context));
        $('div.tab-pane#provisioned ul').each(function () {
            var pending = $('.current-endorsee', this);

            if (pending.length) {
                pending.appendTo($(this));
            }
        });
    }
}
