function initBlurEvents(){
    $('input[id=id_study-0-pubmed_id]').blur(function() {
        var value = $(this).val();
        if(value.length>10 || !value.match(/^\d{0,10}$/ )){
            message1 = 'Pubmed id can consist of at most ten digits.'
            alert(message1);
        }
    });
}