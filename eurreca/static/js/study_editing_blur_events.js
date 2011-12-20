function initBlurEvents(){
    $('input[id=id_study-0-study_id]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>50){
            if(!$(this).hasClass( "invalid" )){
                message1 = 'Study id can consist of at most 50 characters.';            
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-pubmed_id]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(!value.match(/^\d{0,10}$/)){
            if(!$(this).hasClass( "invalid" )){
                message1 = 'Pubmed id can consist of at most ten digits.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-year_of_publication]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(!value.match(/^\d{0,4}$/)){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Year of publication\' field can consist of at most four digits.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-authors]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>200){        
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Authors\' field can consist of at most 200 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-micronutrient]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>200){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Micronutrient\' field can consist of at most 200 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-population]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>200){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Population\' field can consist of at most 200 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-endpoint]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>200){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Health outcome\' field can consist of at most 200 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-paper_title]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>200){
            if(!$(this).hasClass( "invalid" )){
                message1 = 'Paper title can consist of at most 200 characters.';
                alert(message1);    
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-journal_title]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>200){
            if(!$(this).hasClass( "invalid" )){
                message1 = 'Journal title can consist of at most 200 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-study_type]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>200){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Study type\' field can consist of at most 200 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-number_of_participants]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(!value.match(/^\d{0,10}$/)){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Number of participants\' field can consist of at most ten digits.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-comments]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = 'Comments can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
    
    $('input[id=id_study-0-environmental_factor]').blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>200){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Environmental factor\' field can consist of at most 200 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );        
        }
    });
}