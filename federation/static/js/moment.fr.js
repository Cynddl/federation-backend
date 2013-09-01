// moment.js language configuration
// language : french (fr)
// author : John Fischer : https://github.com/jfroffice

moment.lang('fr', {
    months : "janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre".split("_"),
    monthsShort : "janv._févr._mars_avr._mai_juin_juil._août_sept._oct._nov._déc.".split("_"),
    weekdays : "dimanche_lundi_mardi_mercredi_jeudi_vendredi_samedi".split("_"),
    weekdaysShort : "dim._lun._mar._mer._jeu._ven._sam.".split("_"),
    weekdaysMin : "Di_Lu_Ma_Me_Je_Ve_Sa".split("_"),
    longDateFormat : {
        LT : "HH:mm",
        L : "DD/MM/YYYY",
        LL : "D MMMM YYYY",
        LLL : "D MMMM YYYY LT",
        LLLL : "dddd D MMMM YYYY LT"
    },
    calendar : {
        sameDay: "[Aujourd'hui à] LT",
        nextDay: '[Demain à] LT',
        nextWeek: 'dddd [à] LT',
        lastDay: '[Hier à] LT',
        lastWeek: 'dddd [dernier à] LT',
        sameElse: 'L'
    },
    relativeTime : {
        future : "dans %s",
        past : "il y a %s",
        s : "quelques secondes",
        m : "une minute",
        mm : "%d minutes",
        h : "une heure",
        hh : "%d heures",
        d : "un jour",
        dd : "%d jours",
        M : "un mois",
        MM : "%d mois",
        y : "un an",
        yy : "%d ans"
    },
    ordinal : function (number) {
        return number + (number === 1 ? 'er' : '');
    },
    week : {
        dow : 1, // Monday is the first day of the week.
        doy : 4  // The week that contains Jan 4th is the first week of the year.
    }
});


moment.tz.add({
    "zones": {
        "Europe/Paris": [
            "0:9:21 - LMT 1891_2_15_0_1 0:9:21",
            "0:9:21 - PMT 1911_2_11_0_1 0:9:21",
            "0 France WE%sT 1940_5_14_23 1",
            "1 C-Eur CE%sT 1944_7_25 2",
            "0 France WE%sT 1945_8_16_3 2",
            "1 France CE%sT 1977 1",
            "1 EU CE%sT"
        ]
    },
    "rules": {
        "France": [
            "1916 1916 5 14 7 23 2 1 S",
            "1916 1919 9 1 0 23 2 0",
            "1917 1917 2 24 7 23 2 1 S",
            "1918 1918 2 9 7 23 2 1 S",
            "1919 1919 2 1 7 23 2 1 S",
            "1920 1920 1 14 7 23 2 1 S",
            "1920 1920 9 23 7 23 2 0",
            "1921 1921 2 14 7 23 2 1 S",
            "1921 1921 9 25 7 23 2 0",
            "1922 1922 2 25 7 23 2 1 S",
            "1922 1938 9 1 6 23 2 0",
            "1923 1923 4 26 7 23 2 1 S",
            "1924 1924 2 29 7 23 2 1 S",
            "1925 1925 3 4 7 23 2 1 S",
            "1926 1926 3 17 7 23 2 1 S",
            "1927 1927 3 9 7 23 2 1 S",
            "1928 1928 3 14 7 23 2 1 S",
            "1929 1929 3 20 7 23 2 1 S",
            "1930 1930 3 12 7 23 2 1 S",
            "1931 1931 3 18 7 23 2 1 S",
            "1932 1932 3 2 7 23 2 1 S",
            "1933 1933 2 25 7 23 2 1 S",
            "1934 1934 3 7 7 23 2 1 S",
            "1935 1935 2 30 7 23 2 1 S",
            "1936 1936 3 18 7 23 2 1 S",
            "1937 1937 3 3 7 23 2 1 S",
            "1938 1938 2 26 7 23 2 1 S",
            "1939 1939 3 15 7 23 2 1 S",
            "1939 1939 10 18 7 23 2 0",
            "1940 1940 1 25 7 2 0 1 S",
            "1941 1941 4 5 7 0 0 2 M",
            "1941 1941 9 6 7 0 0 1 S",
            "1942 1942 2 9 7 0 0 2 M",
            "1942 1942 10 2 7 3 0 1 S",
            "1943 1943 2 29 7 2 0 2 M",
            "1943 1943 9 4 7 3 0 1 S",
            "1944 1944 3 3 7 2 0 2 M",
            "1944 1944 9 8 7 1 0 1 S",
            "1945 1945 3 2 7 2 0 2 M",
            "1945 1945 8 16 7 3 0 0",
            "1976 1976 2 28 7 1 0 1 S",
            "1976 1976 8 26 7 1 0 0"
        ],
        "C-Eur": [
            "1916 1916 3 30 7 23 0 1 S",
            "1916 1916 9 1 7 1 0 0",
            "1917 1918 3 15 1 2 2 1 S",
            "1917 1918 8 15 1 2 2 0",
            "1940 1940 3 1 7 2 2 1 S",
            "1942 1942 10 2 7 2 2 0",
            "1943 1943 2 29 7 2 2 1 S",
            "1943 1943 9 4 7 2 2 0",
            "1944 1945 3 1 1 2 2 1 S",
            "1944 1944 9 2 7 2 2 0",
            "1945 1945 8 16 7 2 2 0",
            "1977 1980 3 1 0 2 2 1 S",
            "1977 1977 8 0 8 2 2 0",
            "1978 1978 9 1 7 2 2 0",
            "1979 1995 8 0 8 2 2 0",
            "1981 9999 2 0 8 2 2 1 S",
            "1996 9999 9 0 8 2 2 0"
        ],
        "EU": [
            "1977 1980 3 1 0 1 1 1 S",
            "1977 1977 8 0 8 1 1 0",
            "1978 1978 9 1 7 1 1 0",
            "1979 1995 8 0 8 1 1 0",
            "1981 9999 2 0 8 1 1 1 S",
            "1996 9999 9 0 8 1 1 0"
        ]
    },
    "links": {}
});