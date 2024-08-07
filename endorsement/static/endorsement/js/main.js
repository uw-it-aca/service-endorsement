// javascript for service endorsement manager
/* jshint esversion: 6 */

import { MainTabs } from "./tabs.js";
import { Endorse } from "./endorse.js";
import { Revoke } from "./revoke.js";
import { Renew } from "./renew.js";
import { Reasons } from "./reasons.js";
import { EmailEdit } from "./emailedit.js";
import { ClipboardCopy } from "./clipboard.js";
import { TogglePanel } from "./toggle.js";
import { DisplayFilterPanel } from "./filter.js";
import { HandlebarsHelpers } from "./handlebars-helpers.js";
import { ManageProvisionedServices } from "./tab/endorsed.js";
import { ManageSharedNetids } from "./tab/shared.js";
import { ManageOfficeAccess } from "./tab/office.js";
import { ManageSharedDrives } from "./tab/google.js";

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

        panels = [MainTabs,
                  ManageProvisionedServices,
                  ManageSharedNetids,
                  ManageOfficeAccess,
                  ManageSharedDrives];
        loadTools(panels);

        setTabFromPath();
    }
    catch (err) {
        if (err.name !== 'ReferenceError') {
            // not a 401, 404 response
            console.log(err);
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

var setTabFromPath = function () {
    var tabs = [
        {path: '/', tab: 'services'},
        {path: '/access', tab: 'access'},
        {path: '/drives', tab: 'drives'}
    ], tab;

    $.each(tabs, function () {
        if (window.location.pathname === this.path) {
            MainTabs.openTab(this.tab);
            return false;
        }
    });
};
