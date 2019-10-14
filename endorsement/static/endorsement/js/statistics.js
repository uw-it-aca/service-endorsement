// javascript for service endorsement manager
/* jshint esversion: 6 */
import { DateTime } from "./datetime.js";

$(window.document).ready(function() {
    registerEvents();
    getEndorsementServiceStats();
    getEndorsementSharedStats();
    getEndorsementPendingStats();
    getEndorsementEndorsersStats();
    getEndorsementRateStats($('select#daily-rate option:selected').val())
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
    }).on('change', 'select#daily-rate', function (e) {
        var period = $('option:selected', $(this)).val()

        getEndorsementRateStats(period)
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
        series = [],
        pie_data = [];

    $.each(stats.fields, function (i, name) {
        series.push({
            type: 'column',
            stack: 'provisioned',
            name: name,
            data: []
        });
        series.push({
            type: 'column',
            stack: 'revoked',
            name: 'Revoked ' + name,
            data: []
        });
    });

    $.each(stats.data, function () {
        var data = this;

        categories.push(data[0]);
        $.each(stats.fields, function (i) {
            series[i * 2].data.push(data[1][i]);
            series[(i * 2) + 1].data.push(data[2][i]);
        });
    });

    // pie chart distribution data
    $.each(stats.fields, function (i, name) {
        var n = 0;

        $.each(series[i * 2].data, function () {
            n += this;
        });

        pie_data.push({
            name: name,
            y: n,
            color: Highcharts.getOptions().colors[i * 2]
        });
    });

    series.push({
        type: 'pie',
        name: 'Distribution',
        data: pie_data,
        center: [60, 35],
        size: 80,
        showInLegent: false,
        dataLabels: {
            enabled: false
        }
    });

    Highcharts.chart('rate_container', {
        chart: {
            type: 'column',
            zoomType: 'x'
        },
        labels: {
            items: [{
                html: 'Total Provisioned',
                style: {
                    left: '22px',
                    top: '-10px'
                }
            }]
        },
        credits: {
            enabled: false
        },
        title: {
            text: null
        },
        xAxis: [
            {
                categories: categories,
                crosshair: true
            }
        ],
        plotOptions: {
            column: {
                stacking: 'normal',
            }
        },
        series: series
    });
};


var displayStatRateError = function (json) {
    $('#rate_container').html('ERROR: ' + JSON.stringify(json));
};


var getEndorsementRateStats = function (period) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value;

    $.ajax({
        url: "/api/v1/stats/rate/" + parseInt(period),
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
        key;

    if ($.type(stats.data) === 'array') {
        $.each(stats.data, function (i, v) {
            data.push({
                name: v[0],
                y: v[1]
            });
        });
    } else if ($.type(stats.data) === 'object') {
        $.each(stats.data, function (k, v) {
            data.push({
                name: k,
                y: v
            });
        });
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
