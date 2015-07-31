/*
 * timeago: a jQuery plugin, version: 0.9.2 (2010-09-14)
 * @requires jQuery v1.2.3 or later
 *
 * Timeago is a jQuery plugin that makes it easy to support automatically
 * updating fuzzy timestamps (e.g. "4 minutes ago" or "about 1 day ago").
 *
 * For usage and examples, visit:
 * http://timeago.yarp.com/
 *
 * Licensed under the MIT:
 * http://www.opensource.org/licenses/mit-license.php
 *
 * Copyright (c) 2008-2010, Ryan McGeary (ryanonjavascript -[at]- mcgeary [*dot*] org)
 */
(function($) {
  $.timeago = function(timestamp, settings) {
    if (typeof timestamp == "string") timestamp = $.timeago.parse(timestamp);
    else if (!timestamp instanceof Date) timestamp = $.timeago.datetime(timestamp);
    return inWords(timestamp, $.extend(true, {}, $t.settings, settings));
  };
  var $t = $.timeago;

  $.extend($.timeago, {
    settings: {
      refreshMillis: 60000,
      allowFuture: false,
      strings: {
        prefixAgo: null,
        prefixFromNow: null,
        suffixAgo: "전",
        suffixFromNow: null,
        seconds: "%d초",
        minute: "1분",
        minutes: "%d분",
        hour: "한 시간",
        hours: "about %d hours",
        day: "a day",
        days: "%d days",
        month: "about a month",
        months: "%d months",
        year: "about a year",
        years: "%d years",
        numbers: []
      }
    },
    inWords: function(distanceMillis, date, settings) {
      var $l = settings.strings;
      var prefix = $l.prefixAgo;
      var suffix = $l.suffixAgo;
      if (settings.allowFuture) {
        if (distanceMillis < 0) {
          prefix = $l.prefixFromNow;
          suffix = $l.suffixFromNow;
        }
        distanceMillis = Math.abs(distanceMillis);
      }

      var seconds = distanceMillis / 1000;
      var minutes = seconds / 60;
      var newminutes = date.getMinutes()
      var hours = date.getHours();
      var days = date.getDate();
      var month = date.getMonth()+1;
      var years = date.getFullYear();
      var hours_minutes = [hours.toString(), newminutes.toString()].join(":");
      var years_month_date = [years.toString(), month.toString(), days.toString()].join(".");

      function substitute(stringOrFunction, number) {
        var string = $.isFunction(stringOrFunction) ? stringOrFunction(number, distanceMillis) : stringOrFunction;
        var value = ($l.numbers && $l.numbers[number]) || number;
        return string.replace(/%d/i, value);
      }

      var words = seconds < 45 && substitute($l.seconds, Math.round(seconds)) ||
        seconds < 90 && substitute($l.minute, 1) ||
        minutes < 45 && substitute($l.minutes, Math.round(minutes)) ||
        minutes < 90 && substitute($l.hour, 1) ||
        minutes < 1440 && hours_minutes ||
        years_month_date;
      suffix = minutes < 90 && suffix ||
        "";
      return $.trim([prefix, words, suffix].join(" "));
    },
    parse: function(iso8601) {
      var s = $.trim(iso8601);
      s = s.replace(/\.\d\d\d+/,""); // remove milliseconds
      s = s.replace(/-/,"/").replace(/-/,"/");
      s = s.replace(/T/," ").replace(/Z/," UTC");
      s = s.replace(/([\+-]\d\d)\:?(\d\d)/," $1$2"); // -04:00 -> -0400
      return new Date(s);
    },
    datetime: function(elem) {
      // jQuery's `is()` doesn't play well with HTML5 in IE
      var isTime = $(elem).get(0).tagName.toLowerCase() == "time"; // $(elem).is("time");
      var iso8601 = isTime ? $(elem).attr("datetime") : $(elem).attr("timeago");
      return $t.parse(iso8601);
    }
  });

  $.fn.timeago = function(settings) {
    var self = this;
    var $s = $.extend(true, {}, $t.settings, settings);
    self.data("timeago", { settings: $s });
    self.each(refresh);
    if ($s.refreshMillis > 0) {
      setInterval(function() { self.each(refresh); }, $s.refreshMillis);
    }
    return self;
  };

  function refresh() {
    var data = prepareData(this);
    if (!isNaN(data.datetime)) {
      $(this).text(inWords(data.datetime, data.settings));
    }
    return this;
  }

  function prepareData(element) {
    element = $(element);
    var data = element.data("timeago");
    if (!data.datetime) {
        data = $.extend(true, {}, data, { datetime: $t.datetime(element) })
        element.data("timeago", data);
    }
    return data;
  }

  function inWords(date, settings) {
    return $t.inWords(distance(date), date, settings);
  }

  function distance(date) {
    return (new Date().getTime() - date.getTime());
  }

  // fix for IE6 suckage
  document.createElement("abbr");
  document.createElement("time");
})(jQuery);
