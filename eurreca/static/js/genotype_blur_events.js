function initGenotypeBlurEvents( tr ){
    $('input[id=input_gene]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Gene name\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_snp_ref]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'SNP ref\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_snp_variant]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'SNP variant\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_snp_name]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'SNP name\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_allele]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Allele\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_mutation]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Mutation\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_zygosity]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Zygosity\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_number_of_people_with_genotype]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>50){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Number of people with genotype\' field can consist of at most 50 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_genotype_frequency]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Frequency\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_estimated_overal_frequency]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>10){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Estimated overall frequency\' field can consist of at most 10 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
    
    $('input[id=input_genotype_details]', tr ).blur(function() {
        var value = $(this).val();
        value = $.trim(value);
        $(this).val(value);
        if(value.length>500){
            if(!$(this).hasClass( "invalid" )){
                message1 = '\'Genotype details\' field can consist of at most 500 characters.';
                alert(message1);
                $(this).addClass( "invalid" );
            }
        } else {
            $(this).removeClass( "invalid" );
        }
    });
}