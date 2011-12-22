function initPhenotypeBlurEvents( tr ){
    $('input[id=input_phenotype_name]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Name\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_intake_data]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Intake data\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
}