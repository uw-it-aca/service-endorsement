// javascript for service endorsement manager
/* jshint esversion: 6 */
import { DateTime } from "./datetime.js";

$(window.document).ready(function() {
    registerEvents();
    getEndorsementServiceStats();
    getEndorsementSharedStats();
    getEndorsementPendingStats();
});

var registerEvents = function() {
    $(document).on('endorse:EndorsementStatsServiceResult', function (e, stats) {
        displayServiceStats(stats.service);
    }).on('endorse:EndorsementStatsSharedResult', function (e, stats) {
        displaySharedStats(stats.shared);
    }).on('endorse:EndorsementStatsPendingResult', function (e, stats) {
        displayPendingStats(stats.pending);
    });
};

var displayServiceStats = function (stats) {
    pieChartFromSimpleDict('service_container', 'Service Share', 'Services', stats);
};

var displayStatsServiceError = function (json) {
    $('#service_container').html('ERROR: ' + JSON.stringify(json));
};

var getEndorsementServiceStats = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/stats/service",
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:EndorsementStatsServiceResult', [{
                service: results
            }]);
        },
        error: function(xhr, status, error) {
            displayStatsServiceError(xhr.responseJSON);
        }
    });
};


var displaySharedStats = function (stats) {
    pieChartFromSimpleDict('shared_container', 'Netids by Type', 'Netids', stats);
};


var displayStatsSharedError = function (json) {
    $('#shared_container').html('ERROR: ' + JSON.stringify(json));
};


var getEndorsementSharedStats = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/stats/shared",
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:EndorsementStatsSharedResult', [{
                shared: results
            }]);
        },
        error: function(xhr, status, error) {
            displayStatsSharedError(xhr.responseJSON);
        }
    });
};


var displayPendingStats = function (stats) {
    pieChartFromSimpleDict('pending_container', 'Pending Provisions', 'Emails', stats);
};


var displayStatsPendingError = function (json) {
    $('#pending_container').html('ERROR: ' + JSON.stringify(json));
};


var getEndorsementPendingStats = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/stats/pending",
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:EndorsementStatsPendingResult', [{
                pending: results
            }]);
        },
        error: function(xhr, status, error) {
            displayStatsPendingError(xhr.responseJSON);
        }
    });
};


var pieChartFromSimpleDict = function(container, title, series_name, stats) {
    var data = [],
        key, 
        total = 0.00;

    for (key in stats) {
        total += parseFloat(stats[key]);
    }

    if (total > 0) {
        for (key in stats) {
            data.push({
                name: key,
                y: (parseFloat(stats[key])/total) * 100
            });
        }
    }

    Highcharts.chart(container, {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        credits: {
            enabled: false
        },
        title: {
            text: title
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: false
                },
                showInLegend: true
            }
        },
        series: [{
            name: series_name,
            colorByPoint: true,
            data: data
        }]
    });
};
