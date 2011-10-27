/*
The following variables should be declared before inclusion of this .js:

    genotypeCount = {% if genotypeCount %} {{ genotypeCount }} {% else %} 0 {% endif %}
    phenotypeCount = {% if phenotypeCount %} {{ phenotypeCount }} {% else %} 0 {% endif %}
    panelCount = {% if panelCount %} {{ panelCount }} {% else %} 0 {% endif %}
    interactionCount = {% if interactionCount %} {{ interactionCount }} {% else %} 0 {% endif %}

*/

function incCount(id) {
    if(id=='genotype'){
        genotypeCount = genotypeCount + 1;
    }
    if(id=='phenotype'){
        phenotypeCount = phenotypeCount + 1;
    }
    if(id=='panel'){
        panelCount = panelCount + 1;        
    }
    if(id=='interaction'){
        interactionCount = interactionCount + 1;        
    }
}

function getCount(id) {
    if(id=='genotype'){
        return genotypeCount;
    }
    if(id=='phenotype'){
        return phenotypeCount;
    }
    if(id=='panel'){
        return panelCount;        
    }
    if(id=='interaction'){
        return interactionCount;        
    }
}

function addRow(id) {
  strNewRow = '<tr>';
  $('#'+id+'_row').find('th').find('div#variable_name').each(function(){
    strNewRow += "<td id='interactionTable'><input type='text' id='"+id+"-"+getCount(id)+"-"+$(this).html()+"' name='"+id+"-"+getCount(id)+"-"+$(this).html()+"' /></td>"
  });
  strNewRow += '<td id="interactionTable"><a href="#" onClick="saveRow(\''+id+'\',this); return false;">save</a></td>';
  strNewRow += '</tr>';
  $("#"+id).append(strNewRow);
}

function saveRow(id, that) {
  if(id=='interaction') {
    saveInteractionRow();
  }
  strNewRow = '';
  $(that).parents('tr').find('input').each(function(){
    strNewRow += "<td id='interactionTable'>"+$(this).val()+"&nbsp;";
    strNewRow += "<input type='text' id='"+$(this).attr('id')+"' name='"+$(this).attr('name')+"' style='display: none;' value='"+$(this).val()+"' />"
    strNewRow += '</td>';
  });
  strNewRow += '<td id="interactionTable"><a href="#" onClick="editRow(\''+id+'\',this); return false;">edit</a></td>';
  $(that).parents('tr').html(strNewRow);
  incCount(id);
}

function saveInteractionRow() {
  $("#genotype").append(
    "<tr><td id='interactionTable'>"+$('#interaction-'+getCount('interaction')+'-gene').val()+
    "<input type='text' name='genotype-"+getCount('genotype')+"-gene' style='display: none;' value='"+$('#interaction-'+getCount('interaction')+'-gene').val()+"' />"+
    "&nbsp;</td><td id='interactionTable'>"+$('#interaction-'+getCount('interaction')+'-snp_ref').val()+
    "<input type='text' name='genotype-"+getCount('genotype')+"-snp_ref' style='display: none;' value='"+$('#interaction-'+getCount('interaction')+'-snp_ref').val()+"' />"+
    +"&nbsp;</td><td id='interactionTable'>&nbsp;</td>"+
    "<td id='interactionTable'>&nbsp;</td><td id='interactionTable'>"+ 
    "<a href='#' onClick='editRow(\"genotype\",this); return false;'>edit</a></td></tr>");
  incCount('genotype');
  $("#phenotype").append("<tr><td id='interactionTable'>"+$('#interaction-'+getCount('interaction')+'-phenotype_name').val()+
    "<input type='text' name='phenotype-"+getCount('phenotype')+"-phenotype_name' style='display: none;' value='"+$('#interaction-'+getCount('interaction')+'-phenotype_name').val()+"' />"+
    "&nbsp;</td><td id='interactionTable'>&nbsp;</td><td id='interactionTable'>"+
    "<a href='#' onClick='editRow(\"phenotype\",this); return false;'>edit</a></td></tr>");
  incCount('phenotype');
  $("#panel").append("<tr><td id='interactionTable'>"+$('#interaction-'+getCount('interaction')+'-description').val()+
    "<input type='text' name='panel-"+getCount('panel')+"-description' style='display: none;' value='"+$('#interaction-'+getCount('interaction')+'-description').val()+"' />"+
    "&nbsp;</td><td id='interactionTable'>&nbsp;</td><td id='interactionTable'>&nbsp;</td>"+ 
    "<td><a href='#' onClick='editRow(\"panel\",this); return false;'>edit</a></td></tr>");
  incCount('panel');
}

function editRow(id, that) {
  lstHeaders = $('#'+id+'_row').find('th');
  iCounter = 0;
  $(that).parents('tr').find('td').each(function(){
    if(iCounter < lstHeaders.length) {
      oldVal = $(this).html();
      $(this).html("<input type='text' id='"+$(lstHeaders[iCounter]).html()+"'  name='"+$(lstHeaders[iCounter]).html()+"' value='"+oldVal+"' />");
    } else {
      $(this).html('<a href="#" onClick="saveRow(\''+id+'\',this); return false;">save</a>');
    }
    iCounter = iCounter + 1;
  });
}