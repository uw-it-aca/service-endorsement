// javascript for service endorsement manager
/* jshint esversion: 6 */
import { DateTime } from "./datetime.js";

$(window.document).ready(function() {
    registerEvents();
    getEndorsementServiceStats();
    getEndorsementSharedStats();
    getEndorsementPendingStats();
    getEndorsementEndorsersStats();
    getEndorsementRateStats()
});

var registerEvents = function() {
    $(document).on('endorse:EndorsementStatsServiceResult', function (e, stats) {
        displayServiceStats(stats.service);
    }).on('endorse:EndorsementStatsSharedResult', function (e, stats) {
        displaySharedStats(stats.shared);
    }).on('endorse:EndorsementStatsPendingResult', function (e, stats) {
        displayPendingStats(stats.pending);
    }).on('endorse:EndorsementStatsEndorsersResult', function (e, stats) {
        displayEndorsersStats(stats.endorsers);
    }).on('endorse:EndorsementStatsRateResult', function (e, stats) {
        displayRateStats(stats.rate);
    });
};

var displayServiceStats = function (stats) {
    pieChartFromStats('service_container', 'Service Share', 'Services', stats);
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
    pieChartFromStats('shared_container', 'Provisioned Netids by Type', 'Netids', stats);
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
    pieChartFromStats('pending_container', 'Pending Provisions', 'Emails', stats);
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


var displayEndorsersStats = function (stats) {
    var top_stats = {
        total: 0,
        data: stats.data.slice(0,10)
    };

    $.each(top_stats.data, function () {
        top_stats.total += this[1];
    });

    pieChartFromStats('endorsers_container', 'Top 10 Endorsers', 'Endorser', top_stats);
};


var displayStatsEndorsersError = function (json) {
    $('#endorsers_container').html('ERROR: ' + JSON.stringify(json));
};


var getEndorsementEndorsersStats = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/stats/endorsers",
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:EndorsementStatsEndorsersResult', [{
                endorsers: results
            }]);
        },
        error: function(xhr, status, error) {
            displayStatsEndorsersError(xhr.responseJSON);
        }
    });
};


var displayRateStats = function (stats) {
    var categories = [],
        data = [];

    $.each(stats.data, function () {
        categories.push(this[0]);
        data.push(this[1]);
    });

    barChart('rate_container', 'Provisioning Daily Rate', 'Provision Requests', 'Requests', categories, data);
};


var barChart = function (container, title, yTitle, seriesName, categories, data) {
    Highcharts.chart(container, {
        chart: {
            type: 'column'
        },
        title: {
            text: title
        },
        xAxis: {
            categories: categories,
            crosshair: true
        },
        yAxis: {
            min: 0,
            allowDecimals: false,
            title: {
                text: yTitle
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y} Requests</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [{
            name: seriesName,
            data: data
        }]
    });
};


var displayStatRateError = function (json) {
    $('#rate_container').html('ERROR: ' + JSON.stringify(json));
};


var getEndorsementRateStats = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/stats/rate/180",
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $(document).trigger('endorse:EndorsementStatsRateResult', [{
                rate: results
            }]);
        },
        error: function(xhr, status, error) {
            displayStatRateError(xhr.responseJSON);
        }
    });
};


var pieChartFromStats = function (container, title, series_name, stats) {
    var data = [],
        total = parseFloat(stats.total),
        key;

    if (total > 0) {
        if ($.type(stats.data) === 'array') {
            $.each(stats.data, function (i, v) {
                data.push({
                    name: v[0],
                    y: (parseFloat(v[1])/total) * 100
                });
            });
        } else if ($.type(stats.data) === 'object') {
            $.each(stats.data, function (k, v) {
                data.push({
                    name: k,
                    y: (parseFloat(v)/total) * 100
                });
            });
        }
    }

    pieChart(container, title, series_name, data);
};


var pieChart = function(container, title, series_name, data) {
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
