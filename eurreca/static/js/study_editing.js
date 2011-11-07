var interactCache = new Array();

function addRow(id) {
    strNewRow = '<tr>';
    $('#'+id+'_row').find('th').each(function(){
        strNewRow += "<td><input type='text' id='input_"+$(this).attr('id')+"'/></td>"
    });
    strNewRow += '<td><a href="#" onClick="saveRow(\''+id+'\',this); return false;">save</a></td>';
    strNewRow += '</tr>';
    $("#"+id).append(strNewRow);
}

function saveRow(id, that) {
    
    iRowNr = $(that).parents('tr').index();

    if(id=='interaction') {
        arrIndex = saveInteractionRow();
        interactCache[iRowNr] = arrIndex;
    } else {
        $('#interaction tr').each(function() {
            arrIndex = interactCache[$(this).index()];
            if(iRowNr==arrIndex[id+'Nrs']) {
                $(this).css('background-color','red');
            } else {
                $(this).css('background-color','');
            }
            
        });
    }
                    
    strNewRow = '';
    $(that).parents('tr').find('input').each(function(){
        strNewRow += "<td>"+$(this).val()+"</td>";
    });
    strNewRow += '<td><a href="#" onClick="editRow(\''+id+'\',this); return false;">edit</a></td>';
    $(that).parents('tr').html(strNewRow);
}

function saveInteractionRow() {
    iGenotype = null;
    $('#genotype tr').each(function() {
        if($(this).children('td:nth-child(1)').html()==$('#input_genotype-gene').val() && $(this).children('td:nth-child(2)').html()==$('#input_genotype-snp_ref').val() ) {
            iGenotype = $(this).index();
        }
    });
    if(iGenotype==null) {                
        $("#genotype").append("<tr><td>"+$('#input_genotype-gene').val()+"</td><td>"+$('#input_genotype-snp_ref').val()+"</td><td></td><td></td><td><a href='#' onClick='editRow(\"genotype\",this); return false;'>edit</a></td></tr>");
        iGenotype = $("#genotype").find("tr").length-1;
    }
    
    iPhenotype = null;
    $('#phenotype tr').each(function() {
        if($(this).children('td:nth-child(1)').html()==$('#input_phenotype-phenotype_name').val()) {
            iPhenotype = $(this).index();
        }
    });
    if(iPhenotype==null) {                
        $("#phenotype").append("<tr><td>"+$('#input_phenotype-phenotype_name').val()+"</td><td></td><td><a href='#' onClick='editRow(\"phenotype\",this); return false;'>edit</a></td></tr>");
        iPhenotype = $("#phenotype").find("tr").length-1;
    }
    
    iPanel = null;
    $('#panel tr').each(function() {
        if($(this).children('td:nth-child(1)').html()==$('#input_panel-panel_description').val()) {
            iPanel = $(this).index();
        }
    });
    if(iPanel==null) {                
        $("#panel").append("<tr><td>"+$('#input_panel-panel_description').val()+"</td><td></td><td></td><td><a href='#' onClick='editRow(\"panel\",this); return false;'>edit</a></td></tr>");
        iPanel = $("#panel").find("tr").length-1;
    }				
    
    return {"genotypeNrs":iGenotype, "phenotypeNrs":iPhenotype, "panelNrs":iPanel};
}

function editRow(id, that) {
    lstHeaders = $('#'+id+'_row').find('th');
    iCounter = 0;
    $(that).parents('tr').find('td').each(function(){
        if(iCounter < lstHeaders.length) {
            oldVal = $(this).html();
            $(this).html("<input type='text' id='"+$(lstHeaders[iCounter]).html()+"' value='"+oldVal+"'/>");
        } else {
            $(this).html('<a href="#" onClick="saveRow(\''+id+'\',this); return false;">save</a>');
        }
        iCounter = iCounter + 1;
    });
}

function submitData() {
    genotypes = '"genotype":'+submitDataHelper('genotype');

    phenotypes = '"phenotype":'+submitDataHelper('phenotype');
    
    panels =  '"panel":'+submitDataHelper('panel');
    
    //interactions = '"interaction":'+submitDataHelper('interaction');
    interactions = '"interaction":{';
    count = 0;
    coll = $('#interaction tr td:nth-child(5)');
    coll.each(function() {
        rij = this;
        interactions = interactions + '"'+count+'":"'+$(rij).html()+'"';
        count = count + 1;
        if(count!=coll.length){
            interactions = interactions + ',';
        }
    });
    interactions = interactions + '}'
    
    interactionRelations = '"interactionRelations":'+retrieve_interaction_relations();

    returnObject =  '{' + genotypes + "," + phenotypes + "," + panels + ",";
    returnObject += interactions + ',' + interactionRelations + '}'; 
    
    form = $('form[name=study_editing]');
    formstuff = "<input type=hidden name='returnObject' value='";
    form.append(formstuff + returnObject +"'>");
    form.submit();
}

function retrieve_interaction_relations(){
    ret = '{';
    
    for(i=0;i<interactCache.length;i++){
        if(ret.length>1) {
            ret+= ',';
        }
        ret += '"'+i+'":{"genotype":'+interactCache[i]["genotypeNrs"]+',"phenotype":'+interactCache[i]["phenotypeNrs"]+',"panel":'+interactCache[i]["panelNrs"]+'}';
    }
    ret += "}";
    return ret;
}

function submitDataHelper(type){
    headers = []
    $('#'+type+'_row').find('th').each(function(){
        headers.push($(this).attr('id'));
    });
    
    ret = '{';
    count = 0;
    coll = $('#'+type+' tr');
    coll.each(function() {
        string = '';
        count2 = 0;
        coll2 = $(this).children('td:not(:last-child)');
        coll2.each(function() {
            item = $(this).html();
            if(item==''){ item = 'null'; }
            string += '"'+headers[count2]+'":"'+item+'"';
            count2 += 1;
            if(count2!=coll2.length){ string += ","; }
        });
        ret += '"'+count+'":{'+string+'}';
        count += 1;
        if(count!=coll.length){ ret += ","; }
    });
    ret += "}";
    return ret;
}