// javascript for service endorsement manager

$(window.document).ready(function() {
    var common_tools,
        panels;

	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();

    try {
        common_tools = [Endorse,
                        Revoke,
                        Renew,
                        Reasons,
                        EmailEdit,
                        ClipboardCopy,
                        TogglePanel,
                        DisplayFilterPanel];
        loadTools(common_tools);

        panels = [ManageProvisionedServices,
                  ManageSharedNetids];
        loadTools(panels);
    }
    catch (err) {
        if (err.name !== 'ReferenceError') {
            // not a 401, 404 response
            console.error(err);
        }
    }
});

var displayPageHeader = function() {
    var source = $("#page-top").html();
    var template = Handlebars.compile(source);
    $("#top_banner").html(template({
        netid: window.user.netid
    }));
};

var loadTools = function (tools) {
    // load method puts whatever the tool needs in the document,
    // sets up events and so forth...
    $.each(tools, function () {
        this.load.apply(this);
    });
};
