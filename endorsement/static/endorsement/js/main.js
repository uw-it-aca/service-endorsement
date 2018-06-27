// javascript for service endorsement manager

$(window.document).ready(function() {
    var common_tools = [Revoke,
                        Reasons,
                        HashHistory,
                        ClipboardCopy],
        tabs = [ProvisionServices,
                ManageProvisionedServices,
                ManageSharedNetids];
        
	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();

    loadTools(common_tools);
    loadTools(tabs);

    initialFocus(tabs);
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
