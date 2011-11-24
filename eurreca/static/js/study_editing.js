var interactCache = new Array();

/**
 * Adds a new row to the given table
 * @param id		Type of table to edit
 * @param values	(optional) values to put in the input fields
 * @param editable	(optional) whether the row must be editable or not. Defaults to true
 */
function addRow(id, values, editable) {
	if( values == undefined ) {
		values = [];
	}
	if( editable == undefined ) {
		editable = true;
	}
	
	// Create a new row
	var row = $( '<tr></tr>' );
	
    // Append each input element to the tr
	i = 0;
    $('#'+id+'_row').find('th').each(function(){
    	if( values.length > i )
    		newVal = values[i];
    	else
    		newVal = "";
    	
    	var cell = $( "<td class='editable'></td>" );
    	
    	if( editable ) {
    		cell.append( $( "<input class='newVal' type='text' id='input_" + $(this).attr('id') + "'/>" ).val( newVal ) );
    	} else {
    		cell.text( newVal );
    	}
    	
    	row.append( cell );
    	i++;
    });
    
    row.append( '<td class="buttons">' + ( editable ? rowEditingButtons( id, false ) : rowDefaultButtons( id ) ) + '</td>' );
    
    $("#"+id).append(row);
}

function saveRow(id, that) {
    
    iRowNr = $(that).parents('tr').index();

    if(id=='interaction') {
        arrIndex = saveInteractionRow();
        interactCache[iRowNr] = arrIndex;
    } else {
        iRowNr = $(that).parents('tr').index();
        // Update relevant interaction rows
        // Right now only works with one object rather than with a list of objects
        $('#interaction tr').each(function() {
            arrIndex = interactCache[$(this).index()];
            if(arrIndex != undefined && iRowNr==arrIndex[id+'Nrs']) {
                delete arrIndex[id+'Nrs'];
                if(id=='genotype'){
                    $(this).children('td:nth-child(1)').html($(that).parents('tr').children('td:nth-child(1)').find('input.newVal').val());
                    $(this).children('td:nth-child(2)').html($(that).parents('tr').children('td:nth-child(2)').find('input.newVal').val());
                    $(this).children('td:nth-child(3)').html($(that).parents('tr').children('td:nth-child(3)').find('input.newVal').val());
                }
                if(id=='phenotype'){
                    $(this).children('td:nth-child(4)').html($(that).parents('tr').children('td:nth-child(1)').find('input.newVal').val());
                    $(this).children('td:nth-child(5)').html($(that).parents('tr').children('td:nth-child(2)').find('input.newVal').val());
                    $(this).children('td:nth-child(6)').html($(that).parents('tr').children('td:nth-child(3)').find('input.newVal').val());
                }
                if(id=='panel'){
                    $(this).children('td:nth-child(4)').html($(that).parents('tr').children('td:nth-child(1)').find('input.newVal').val());
                }
            }
        });
    }

    // Now put all edited text into the td
    strNewRow = '';
    $(that).parents('tr').find( 'td.editable' ).each(function(){
    	var newVal = $('input.newVal', $(this)).val();
    	$(this).text( newVal );
    });
    
    // Replace the buttons with the correct ones
    $(that).parents('tr').find( "td.buttons" ).html( rowDefaultButtons( id ) );
}

function saveInteractionRow() {
    iGenotype = null;
    $('#genotype tr').each(function() {
        if($(this).children('td:nth-child(1)').html()==$('#input_genotype-gene').val() && $(this).children('td:nth-child(2)').html()==$('#input_genotype-snp_ref').val() && $(this).children('td:nth-child(3)').html()==$('#input_genotype-snp_variant').val() ) {
            iGenotype = $(this).index();
        }
    });
    if(iGenotype==null) {      
    	addRow( "genotype", [
    	                     $('#input_genotype-gene').val(),
    	                     $('#input_genotype-snp_ref').val(),
    	                     $('#input_genotype-snp_variant').val(), 
    	], false );
        iGenotype = $("#genotype").find("tr").length-1;
    }
    
    iPhenotype = null;
    $('#phenotype tr').each(function() {
        if($(this).children('td:nth-child(1)').html()==$('#input_phenotype-phenotype_name').val() && $(this).children('td:nth-child(2)').html()==$('#input_phenotype-environmental_factor').val() && $(this).children('td:nth-child(3)').html()==$('#input_phenotype-type').val()) {
            iPhenotype = $(this).index();
        }
    });
    if(iPhenotype==null) {                
    	addRow( "phenotype", [
    	                     $('#input_phenotype-phenotype_name').val(),
    	                     $('#input_phenotype-environmental_factor').val(),
    	                     $('#input_phenotype-type').val(),
    	], false );
        iPhenotype = $("#phenotype").find("tr").length-1;
    }
    
    iPanel = null;
    $('#panel tr').each(function() {
        if($(this).children('td:nth-child(1)').html()==$('#input_panel-panel_description').val()) {
            iPanel = $(this).index();
        }
    });
    if(iPanel==null) {                
    	addRow( "panel", [
     	                     $('#input_panel-panel_description').val()
     	], false );
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
            
            // Determine the id of the new input field
            var newId;
            if(id == 'interaction'){
                newId = "input_"+$('#'+id+'_row').children('th:nth-child('+(iCounter+1)+')').attr('id')
            } else {
            	newId = $(lstHeaders[iCounter]).html();
            }
            
            // Create a text field to edit this value. Assign id and value this way, so escaping is
            // done properly
            var newInput = $( "<input type='text' class='newVal'>" ).attr( "id", newId ).val( oldVal );
            
            // Create a hidden field with the old value in it, so the edit can be cancelled anytime
            var hiddenOldValue = $( "<input type='hidden' class='oldVal'>" ).val( oldVal );
            
            // Replace the current cell with these contents
            $(this).html(newInput).append( hiddenOldValue );
        } else {
            $(this).html( rowEditingButtons( id, true ) );
        }
        iCounter = iCounter + 1;
    });
}

/**
 * Cancels the edits the user made to the given row
 * @param id	type of row to edit ('genotype', 'phenotype', 'panel' or 'interaction'
 * @param that	The link that is clicked on. (is used to retrieve the row we are editing)
 */
function cancelEdit( id, that ) {
    iRowNr = $(that).parents('tr').index();
                    
    $(that).parents('tr').find('td').each(function() {
    	var oldVal = $('input.oldVal', $(this)).val();
    	$(this).text( oldVal );
    });
    
    // Replace the buttons with the correct ones
    $(that).parents('tr').find( "td.buttons" ).html( rowDefaultButtons( id ) );
}

function removeRow(id, that) {
    if(id=='interaction'){
        iRowNr = $(that).parents('tr').index();
        delete interactCache[iRowNr];
        // Now the interactCache object keys no longer match the tr indexes...
        // Reorganise interactCache
        newCache = {}
        new_key = 0
        for(var key in interactCache){
            if(key>iRowNr){
                // This key comes after the removed tr's key
                // This means that the key no longer matches it's tr's index
                newCache[new_key] = interactCache[key]
            } else {
                newCache[key] = interactCache[key]
            }
            new_key++
        }
        for(var key in interactCache){
            delete interactCache[key];
        }
        for(var key in newCache){
            interactCache[key] = newCache[key]
        }
    } else {
        iRowNr = $(that).parents('tr').index();
        // Update relevant interaction rows
        
        // Right now only works with one object rather than with a list of objects
        $('#interaction tr').each(function() {
            arrIndex = interactCache[$(this).index()];
            if(arrIndex != undefined) {
            	if( iRowNr == arrIndex[id+'Nrs']) {
                	// If the entity to remove is part of an interaction, remove it from the interaction
	                delete arrIndex[id+'Nrs'];
	                if(id=='genotype'){
	                    $(this).children('td:nth-child(1)').html('');
	                    $(this).children('td:nth-child(2)').html('');
	                    $(this).children('td:nth-child(3)').html('');
	                }
	                if(id=='phenotype'){
	                    $(this).children('td:nth-child(4)').html('');
	                    $(this).children('td:nth-child(5)').html('');
	                    $(this).children('td:nth-child(6)').html('');
	                }
	                if(id=='panel'){
	                    $(this).children('td:nth-child(7)').html('');
	                }
                } else if( iRowNr < arrIndex[id+'Nrs'] ) {
                	// If the entity to remove is in the list before the entity in the interaction
                	// update the interaction to reflect the changes
                	arrIndex[id+'Nrs']--;
                }
            }
        });
    }
    $(that).parents('tr').remove();
}

function submitData() {
    genotypes = '"genotype":'+submitDataHelper('genotype');
    phenotypes = '"phenotype":'+submitDataHelper('phenotype');
    panels =  '"panel":'+submitDataHelper('panel');
    returnObject =  '{' + genotypes + "," + phenotypes + "," + panels + ",";
    
    interactions = '"interaction":{';
    count = 0;
    coll = $('#interaction tr');
    coll.each(function() {
        rij = '{'
        
        coll2 = $(this).children('td:not(:last-child)');
        coll2.each(function() {
            i = $(this).index();
            if(i>6){
                title = '';
                postfix = '';
                if(i==7){title = 'statistical_model'; postfix = ',';}
                if(i==8){title = 'p_value'; postfix = ',';}
                if(i==9){title = 'ratio_type'; postfix = ',';}
                if(i==10){title = 'ratio'; postfix = ',';}
                if(i==11){title = 'ci_lower'; postfix = ',';}
                if(i==12){title = 'ci_upper'; postfix = ',';}
                if(i==13){title = 'significant_associations';}
                item = $(this).html();
                if(item==''){ item = 'null'; }
                rij += '"'+title+'":"'+item+'"'+postfix;
                //console.log('i:'+i+'\ntitle:'+title+'\nitem:'+item+'\ncount2'+count2+'\nsso far:'+rij);
            }
        });
        
        rij += '}'
        
        interactions = interactions + '"'+count+'":'+rij;
        
        count = count + 1;
        if(count!=coll.length){
            interactions = interactions + ',';
        }
    });
    interactions = interactions + '}'
    
    interactionRelations = '"interactionRelations":'+retrieve_interaction_relations();
    
    returnObject += interactions + ',' + interactionRelations + '}'; 
    
    form = $('form[name=study_editing]');
    formstuff = "<input type=hidden name='returnObject' value='";
    form.append(formstuff + returnObject +"'>");
    form.submit();
}

function retrieve_interaction_relations(){
    ret = '{';
    for(i=0;i<interactCache.length;i++){
        if(interactCache[i]!=undefined){
            if(ret.length>1) {
                ret+= ',';
            }
            gts = -1;
            if(interactCache[i]["genotypeNrs"]!=undefined){
                gts = interactCache[i]["genotypeNrs"];
            }
            pts = -1;
            if(interactCache[i]["phenotypeNrs"]!=undefined){
                pts = interactCache[i]["phenotypeNrs"];
            }
            panels = -1;
            if(interactCache[i]["panelNrs"]!=undefined){
                panels = interactCache[i]["panelNrs"];
            }
            ret += '"'+i+'":{"genotype":'+gts+',"phenotype":'+pts+',"panel":'+panels+'}';
        }
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

/**
 * Returns the HTML for buttons to edit a row in one of the tables
 * @param id	Type of entity to edit
 * @returns {String}
 */
function rowDefaultButtons( id ) {
    return '<a href="#" onClick="editRow(\''+id+'\',this); return false;">edit</a>&nbsp;<a href="#" onClick="removeRow(\''+id+'\',this); return false;">remove</a>';
}

/**
 * Returns the HTML for buttons to show when editing a row
 * @param id	Type of entity to edit
 * @param editing	True if the buttons are used for editing a row, false if the buttons are used for adding a row
 * @returns {String}
 */
function rowEditingButtons( id, editing ) {
	var strHTML = '<a href="#" onClick="saveRow(\''+id+'\',this); return false;">save</a>&nbsp;';
	
	if( editing ) {
		strHTML += '<a href="#" onClick="cancelEdit(\''+id+'\',this); return false;">cancel</a>';
	} else {
		strHTML += '<a href="#" onClick="removeRow(\''+id+'\',this); return false;">cancel</a>';
	}
	
	return strHTML;
}
