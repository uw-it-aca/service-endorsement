// javascript for service endorsement manager

$(window.document).ready(function() {
    var common_tools,
        tabs;

	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();

    try {
        common_tools = [Endorse,
                        Revoke,
                        Reasons,
                        HashHistory,
                        ClipboardCopy,
                        TogglePanel,
                        DisplayFilterPanel];
        loadTools(common_tools);

        tabs = [ProvisionServices,
                ManageProvisionedServices,
                ManageSharedNetids];
        loadTools(tabs);

        initialFocus(tabs);
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

var initialFocus = function (tabs) {
    if (window.location.hash.length === 0) {
        HashHistory.replace('#provision');
        $('#netid_list:visible').focus();
    } else {
        $.each(tabs, function () {
            this.focus.apply(this);
        });
    }
};
