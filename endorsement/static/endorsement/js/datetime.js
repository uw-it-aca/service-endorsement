// javascript for common time and date functions
/* jshint esversion: 6 */

var DateTime = (function () {
    return {
        utc2local: function (utc_date) {
            var local = null,
                utc;

            if (utc_date) {
                utc = moment.utc(utc_date).toDate();
                local = moment(utc).local().format('YYYY-MM-DD HH:mm:ss');
            }

            return local;
        },

        utc2localdate: function (utc_date) {
            var local = null,
                utc;

            if (utc_date) {
                utc = moment.utc(utc_date).toDate();
                local = moment(utc).local().format('MM/DD/YYYY');
            }

            return local;
        }
    };
})();

export { DateTime };
