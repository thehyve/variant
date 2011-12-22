function initPanelBlurEvents( tr ){
    $('input[id=input_panel_description]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Panel description\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_number_of_participants]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>50){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Number of participants\' field can consist of at most 50 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_additional_age_description]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Additional age description\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_mean_age]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>10){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Mean age\' field can consist of at most 10 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
}