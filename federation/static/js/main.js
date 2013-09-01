// Date & time inputs
// --------------------------------------------------

moment.lang('fr', {
    calendar: {
        sameDay: "[Aujourd'hui à] LT",
        nextDay: '[Demain à] LT',
        nextWeek: 'dddd [à] LT',
        lastDay: '[Hier à] LT',
        lastWeek: 'dddd [dernier à] LT',
        sameElse: 'DD MMMM YYYY [à] LT'
    }
});

$(function(){
    $('.datepicker').each(function() {
        var datetime_field = $('input[name="' + $(this).attr('name').replace('date', 'datetime') + '"]');
        var time_field = $('input[name="' + $(this).attr('name').replace('date', 'time') + '"]');

        var val = datetime_field.val();
        date = (!val || !moment(val).isValid()) ? null : moment(val).toDate();
        $(this).pickadate({
            //min: new Date(), // Now
            hiddenSuffix: '_data',
            formatSubmit: 'yyyy-mm-dd',

            onStart: function() {
                if(date) {
                    this.set( 'select', date ); // Set to current or saved date on load
                    time_field.val( moment(val).tz('Europe/Paris').format('HH:mm') );

                    date = moment(this.get('select', 'yyyy-mm-dd') + ' ' + time_field.val());
                    $(datetime_field).val( date.unix() );
                }
            },
            onSet: function() {
                // Update hidden datetime field
                date = moment(this.get('select', 'yyyy-mm-dd') + ' ' + time_field.val());
                $(datetime_field).val( date.unix() );
            }
        });
    });

    if($('#date_first').length > 0){
        var picker_first = $('#date_first').pickadate('picker');
        var picker_last = $('#date_last').pickadate('picker');

        var picker_first_val = picker_first.get('value');
        picker_first.on('set', function(event) {
            if(picker_last.get('value') == '' || picker_last.get('value') == picker_first_val)
                picker_last.set('select', this.get('select'));
            picker_first_val = picker_first.get('value');
        });
    }

    $('.selectize').selectize({
        create: true,
        hideSelected: false,
    });
    
    function match_time (s) {
        var match_1 = /([01]?[0-9]|2[0-3]):([0-5][0-9])/;
        var match_2 = /([01]?[0-9]|2[0-3])h([0-5][0-9])/;
        var match_3 = /([01]?[0-9]|2[0-3])/;

        var result_1 = s.match(match_1),
            result_2 = s.match(match_2),
            result_3 = s.match(match_3);
        var new_val = ''
        if(result_1 != null && result_1.length == 3)
            new_val = result_1[1] + ':' + result_1[2];
        else if(result_2 != null && result_2.length == 3)
            new_val = result_2[1] + ':' + result_2[2];
        else if(result_3 != null && result_3.length == 2)
            new_val = result_3[1] + ':00';

        if(new_val.length == 4) new_val = '0' + new_val;
        return new_val;
    }

    $('.timepicker').focusout(function(){
        this.value = match_time(this.value);

        var date_picker = $('input[name="' + $(this).attr('name').replace('time', 'date') + '"]').pickadate('picker');
        var datetime_field = $('input[name="' + $(this).attr('name').replace('time', 'datetime') + '"]')

        date = moment(date_picker.get('select', 'yyyy-mm-dd') + ' ' + this.value);
        $(datetime_field).val( date.unix() );
    });
});


/**
 * modalEffects.js v1.0.0
 * http://www.codrops.com
 *
 * Licensed under the MIT license.
 * http://www.opensource.org/licenses/mit-license.php
 * 
 * Copyright 2013, Codrops
 * http://www.codrops.com
 */

$(function(){
    var overlay = $('.md-overlay');

    $('.md-trigger').each(function() {
        var el = $(this);
        var modal = $('#' + el.attr('data-modal')),
            close = modal.find('.md-close');

        el.click(function(ev) {
            ev.preventDefault();
            $(modal).addClass('md-show');
        });

        close.click(function(ev) {
            ev.preventDefault();
            $(modal).removeClass('md-show');
        });

    });
});