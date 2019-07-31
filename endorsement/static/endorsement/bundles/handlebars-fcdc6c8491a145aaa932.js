/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 1);
/******/ })
/************************************************************************/
/******/ ({

/***/ "./endorsement/static/endorsement/js/handlebars-helpers.js":
/*!*****************************************************************!*\
  !*** ./endorsement/static/endorsement/js/handlebars-helpers.js ***!
  \*****************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("$(window.document).ready(function() {\n\n    Handlebars.registerPartial({\n        'validation_partial':  $(\"#validation_partial\").html(),\n        'reasons_partial': $(\"#reasons_partial\").html(),\n        'endorsement_row_partial': $(\"#endorsement_row_partial\").html(),\n        'endorse_button_partial': $(\"#endorse_button_partial\").html(),\n        'display_filter_partial': $(\"#display_filter_partial\").html(),\n        'email_editor_partial': $(\"#email_editor_partial\").html(),\n        'enumerate_partial': $(\"#enumerate_partial\").html()\n    });\n\n    Handlebars.registerHelper({\n        'endorsable': function(o365, google) {\n            if ((o365 && this.o365.eligible) ||\n                (google && this.google.eligible)) {\n                return 'checked=\"checked\"';\n            } else {\n                return 'disabled=\"1\"';\n            }\n        },\n        'endorsed': function(endorsements, options) {\n            return (endorsements &&\n                    ((endorsements.o365 && endorsements.o365.datetime_endorsed !== null) ||\n                     (endorsements.google && endorsements.google.datetime_endorsed !== null))) ? options.fn(this) : options.inverse(this);\n        },\n        'reason': function(endorsements, reason, options) {\n            if (endorsements) {\n                if (endorsements.o365 && endorsements.o365.reason) {\n                    return endorsements.o365.reason;\n                } else if (endorsements.google && endorsements.google.reason) {\n                    return endorsements.google.reason;\n                }\n            }\n\n            return \"\";\n        },\n        'has_reason': function(endorsements, options) {\n            return (!(endorsements &&\n                      ((endorsements.o365 && endorsements.o365.reason.length) ||\n                       (endorsements.google && endorsements.google.reason.length)))) ? options.fn(this) : options.inverse(this);\n        },\n        'revokable': function(o365, google) {\n            if ((o365 && this.o365.eligible) ||\n                (google && this.google.eligible)) {\n                return 'checked=\"checked\"';\n            } else {\n                return 'disabled=\"1\"';\n            }\n        },\n        'subscription_context': function(context, netid, svc) {\n            var new_context = context;\n            new_context.netid = netid;\n            new_context.svc = svc;\n            return new_context;\n        },\n        'plural': function(n, singular, plural) {\n            if (n === 1) { \n                return singular;\n            }\n\n            return plural;\n        },\n        'single_endorsement': function(o365, google, options) {\n            if (o365 && Object.keys(o365).length === 1 &&\n                google && Object.keys(google).length === 1 &&\n                o365[Object.keys(o365)[0]] === google[Object.keys(google)[0]]) {\n                return options.fn(this);\n            }\n\n            return options.inverse(this);\n        },\n        'equals': function(a, b, options) {\n            return (a == b) ? options.fn(this) : options.inverse(this);\n        },\n        'gt': function(a, b, options) {\n            return (a > b) ? options.fn(this) : options.inverse(this);\n        },\n        'ifAndNot': function(a, b, options) {\n            return (a && !b) ? options.fn(this) : options.inverse(this);\n        }\n    });\n});\n\n\n//# sourceURL=webpack:///./endorsement/static/endorsement/js/handlebars-helpers.js?");

/***/ }),

/***/ 1:
/*!***********************************************************************!*\
  !*** multi ./endorsement/static/endorsement/js/handlebars-helpers.js ***!
  \***********************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("module.exports = __webpack_require__(/*! ./endorsement/static/endorsement/js/handlebars-helpers.js */\"./endorsement/static/endorsement/js/handlebars-helpers.js\");\n\n\n//# sourceURL=webpack:///multi_./endorsement/static/endorsement/js/handlebars-helpers.js?");

/***/ })

/******/ });