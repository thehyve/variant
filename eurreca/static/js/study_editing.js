var interactCache = new Array();

function switchToTab(tabNum){
    // Counting starts at zero.
    var $tabs = $('#pagetabs').tabs();
    $tabs.tabs('select', tabNum);        
};

/**
 * Adds a new row to the given table for editing
 * @param id		Type of table to edit	(genotype, phenotype or panel)
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
    		var fieldName = $(this).attr('id'); 
    		var input = $( "<input class='newVal' type='text' id='input_" + fieldName + "'/>" ).val( newVal );
    		
    		if( availableFields && availableFields[ fieldName ] ) {
    			cell.append( $( "<div class='autofill' rel=\"" + fieldName + "\"></div" ).append( input ) );
    		} else {
    			cell.append( input );
    		}
    			
    	} else {
    		cell.html( newVal );
    	}
    	
    	row.append( cell );
    	i++;
    });
    
    row.append( '<td class="buttons">' + ( editable ? rowEditingButtons( id, false ) : rowDefaultButtons( id ) ) + '</td>' );
    
    $("#"+id).append(row);
    
    initAutoFill( row );
}


/**
 * Starts editing a row with data in the given table
 * @param id		Type of table to edit	(genotype, phenotype or panel)
 * @param that		Reference to the link clicked (or any other element in the tr that is being edited
 */
function editRow(id, that) {
    lstHeaders = $('#'+id+'_row').find('th');
    iCounter = 0;
    var tr = $(that).parents( "tr" );
    
    tr.find('td').each(function(){
        if(iCounter < lstHeaders.length) {
            oldVal = $(this).html();
            
            
            // Determine the id of the new input field
            var newId;
            var fieldName;
            fieldName = $('#'+id+'_row').children('th:nth-child('+(iCounter+1)+')').attr('id');
            newId = "input_" + fieldName;
            
            // Create a text field to edit this value. Assign id and value this way, so escaping is
            // done properly
            var newInput = $( "<input type='text' class='newVal'>" ).attr( "id", newId ).val( oldVal );
            
            // Create a hidden field with the old value in it, so the edit can be cancelled anytime
            var hiddenOldValue = $( "<input type='hidden' class='oldVal'>" ).val( oldVal );
            
    		if( availableFields && availableFields[ fieldName ] ) {
    			$(this).html( $( "<div class='autofill' rel=\"" + fieldName + "\"></div" ).append( newInput ) );
    		} else {
    			$(this).html( newInput );
    		}
            
            // Replace the current cell with these contents
            $(this).append( hiddenOldValue );
        } else {
            $(this).html( rowEditingButtons( id, true ) );
        }
        iCounter = iCounter + 1;
    });
    
    initAutoFill( tr );
}

/**
 * Saves a row that has been edited in the given table
 * @param id		Type of table to save	(genotype, phenotype or panel)
 * @param that		Reference to the link clicked (or any other element in the tr that is being saved)
 */
function saveRow(id, that) {
    var trs = $(that).parents('tr'); 
    iRowNr = trs.index();

    if(id=='interaction') {
        arrIndex = saveInteractionRow();
        interactCache[iRowNr] = arrIndex;
    } else {
        // Check form constraints and show relevant alerts
        if( checkFormConstraints( trs.children('td'), true ) ) {
            iRowNr = trs.index();
            
            // List of fields to update if an object has been changed
            var listToUpdate = getFieldsToUpdate();
            
            // Update relevant interaction rows
            // Right now only works with one object rather than with a list of objects
            $('#interaction tr').each(function() {
                arrIndex = interactCache[$(this).index()];
                if(arrIndex != undefined && iRowNr==arrIndex[id+'Nrs']) {

                    // Update the fields in the interaction table
                    var td = $("td.editable_" + id, this);
                    
                    var sourceTds = trs.children();
                    for( i = 0; i < listToUpdate[ id ].length; i++ ) {
                        var value = sourceTds.eq(i).find('input.newVal').val();
                        $( listToUpdate[ id ][ i ], td ).val( $.trim(value) );
                    }
                    updateFields( td );
                }
            });
            
            // Now put all edited text into the td
            strNewRow = '';
            trs.find( 'td.editable' ).each(function(){
                var newVal = $('input.newVal', $(this)).val();
                $(this).html( newVal );
            });
            
            // Replace the buttons with the correct ones
            trs.find( "td.buttons" ).html( rowDefaultButtons( id ) );
        }
    }
}

/**
 * Cancels the edits the user made to the given row
 * @param id	type of row to edit ('genotype', 'phenotype', 'panel' )
 * @param that	The link that is clicked on. (is used to retrieve the row we are editing)
 */
function cancelEdit( id, that ) {
    iRowNr = $(that).parents('tr').index();
                    
    $(that).parents('tr').find('td').each(function() {
    	var oldVal = $('input.oldVal', $(this)).val();
    	$(this).html( oldVal );
    });
    
    // Replace the buttons with the correct ones
    $(that).parents('tr').find( "td.buttons" ).html( rowDefaultButtons( id ) );
}

/**
 * Removes a row from the table
 * @param id		id of the table to remove a row from ('genotype', 'phenotype', 'panel' or 'interaction' )
 * @param that		Reference to the link clicked (or any other element in the tr that is being edited)
 */
function removeRow(id, that) {
    var iRowNr = $(that).parents('tr').index();
    if(id=='interaction'){
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
        // Update relevant interaction rows
        
        // Right now only works with one object rather than with a list of objects
        $('#interaction tr').each(function() {
            arrIndex = interactCache[$(this).index()];
            if(arrIndex != undefined) {
            	if( iRowNr == arrIndex[id+'Nrs']) {
                	// If the entity to remove is part of an interaction, remove it from the interaction
	                delete arrIndex[id+'Nrs'];
	                
	                // Clear the fields in the interaction to reflect the deleted entity
	                $( "td.editable_" + id , this).find( "input[type=text]" ).val( "" );
	                $( "td.editable_" + id , this).find( "a.all" ).html( "" );
                } else if( iRowNr < arrIndex[id+'Nrs'] ) {
                	// If the entity to remove is in the list before the entity in the interaction
                	// update the interaction to reflect the changes
                	arrIndex[id+'Nrs']--;
                }
            }
        });
    }
    
    // Actually remove the row 
    $(that).parents('tr').remove();
}

function saveInteractionRow() {
	// Create a row with the newly added element above the 'addNew' row. Do so by copying 
	// the addNew row and replacing the inputs with links
	var addNewRow = $( "#interactionTable .addNew" );
    
    // First destroy the autofill options, since they can not be cloned
    // See http://bugs.jqueryui.com/ticket/5866
    destroyAutoFill( "#interactionTable" );	
    
    var newRow = addNewRow.clone( true, true ).removeClass( "addNew" );
    
    // Replace the input.all elements with links
    newRow.find( "input.all" ).each( function( idx, el ) {
        // Create a new link
        var link = $( "<a class='all' href='#'></a>" ).html( $(el).val() );
        link.click( function(event) { 
            showFormByElement( this ); return false; 
        } );
        
        // Replace the input element with a link
        $(el).before( link )
        $(el).remove();
    });
    
    // Replace the 'save' link with a 'remove' link
    var buttonsCell = newRow.find( "td.buttons" );
    buttonsCell.empty();
    buttonsCell.append( 
            $( "<a href='#'>remove</a>" ).click( function(event) { removeRow( 'interaction', this ); return false; } )
    );
    
    // Insert the new row
    addNewRow.before( newRow );
    
    // Add the autofill lists to the copied elements again
    initAutoFill( "#interactionTable" );

    // Clear the addNew row, so a new row can be inserted
    $( "input", addNewRow ).not("[type=button]").val( "" );
    
    // Now update the interaction cache. To do that, check whether the inserted genotypes and phenotypes already exist.
    return updateObjectsBasedOnInteraction( newRow );
}

function getFieldsToUpdate() {
    return {
			"genotype": [
	 	 	    "input[name=genotype-gene]",
	 		    "input[name=genotype-snp_ref]",
	 		    "input[name=genotype-snp_variant]"
	 		],
	 		"phenotype": [
	 		    "input[name=phenotype-phenotype_name]",
	 	 	    "input[name=phenotype-intake_data]",
	 	 	],
	 	 	"panel": [
	 	 	    "input[name=panel-panel_description]"
	 		]
        };
}

function findOrAddMatchingObjects( objects ) {
    var returnMap = new Array();
	for( key in objects ) {
		var iEl = findOrAddMatchingObject( key, objects[ key ] );
		if( iEl != null )
			returnMap[ key + "Nrs" ] = iEl;
	}
	
	return returnMap;
}

function findOrAddMatchingObject( id, listToCheck ) {
	var iElement = null;
	
	// If any of the values in listToCheck is empty, don't add anything
	var isEmpty = true;
	for( i = 0; i < listToCheck.length; i++ ) {
		if( listToCheck[ i ] != "" ) {
			isEmpty = false;
			break;
		}
	}
	
	if( isEmpty ) {
		return null;
	}
	
	// Loop through all existing objects
    $('#' + id + ' tr').each(function() {
    	var rowFound = true;
    	var tds = $(this).children( "td" );
    	for( i = 0; i < listToCheck.length; i++ ) {
    		if( listToCheck[ i ] != tds.eq( i ).text() ) {
    			rowFound = false;
    			break;
    		}
    	}
    	
    	if( rowFound ) 
    		iElement = $(this).index();
    });
	
    if( iElement==null ) {      
        addRow( id, listToCheck, false );
        iElement = $( "#" + id ).find("tr").length-1;
    }
    
    return iElement;
}

function submitData() {
    
    // Check if all required study fields have been set.
    var required_fields_set = true;
    var coll = $('#studyInformation tr td.contains_required_inputs');
    coll.each(function() {
        $( this ).children('input').each( function( idx, el ) {
            if( $.trim( $(el).val() ) == "" ) {
                $(el).addClass( "invalid" );
                required_fields_set = false;
            } else {
                $(el).removeClass( "invalid" );
            }
        });
    });
    if(required_fields_set==false){
        // Not all are set. Alert user and move to the tab in question.
        alert('Some required fields in the study section are not filled in.');
        switchToTab(0)
        return false;
    }
    
    return_map = {}
    return_map['genotype'] = submitDataHelper('genotype');
    return_map['phenotype'] = submitDataHelper('phenotype');
    return_map['panel'] = submitDataHelper('panel');
    
    var interactionsArray = {};
    var interactionIdx = 0;
    $( "#interaction tr" ).not( ".addNew" ).each( function(idx,row) {
    	var interaction = {};
    	
    	// Loop through all input elements
    	$( ".editable_ratios input[type=text]", $(row) ).not( ".all" ).each( function( idx, input ) {
    		interaction[ $(input).attr( 'name' ) ] = $(input).val();
    	});
    	
    	interactionsArray[ interactionIdx++ ] = interaction;
    });
    
    return_map['interaction'] = interactionsArray;
    return_map['interactionRelations'] = retrieve_interaction_relations();
    return_object = JSON.stringify(return_map);
    // Replace ' with ` to deal with crappy Python/Django JSON decoding /
    // POST handling
    // ' should actally not be a problem according to JSON specification
    return_object = return_object.replace(/'/g, "`");
    form = $('form[name=study_editing]');
    formstuff = "<input type=hidden name='returnObject' value='";
    form.append(formstuff + return_object +"'>");
    form.submit();
}

function retrieve_interaction_relations(){
    ret_map = {}
    for(i=0;i<interactCache.length;i++){
        if(interactCache[i]!=undefined){
            ret_map[""+i] = {}
            gts = -1;
            pts = -1;
            panels = -1;
            if(interactCache[i]["genotypeNrs"]!=undefined){
                gts = interactCache[i]["genotypeNrs"];
            }
            if(interactCache[i]["phenotypeNrs"]!=undefined){
                pts = interactCache[i]["phenotypeNrs"];
            }
            if(interactCache[i]["panelNrs"]!=undefined){
                panels = interactCache[i]["panelNrs"];
            }
            ret_map[""+i]['genotype'] = gts;
            ret_map[""+i]['phenotype'] = pts;
            ret_map[""+i]['panel'] = panels;
        }
    }
    return ret_map;
}

function submitDataHelper(type){
    headers = []
    $('#'+type+'_row').find('th').each(function(){
        headers.push($(this).attr('id'));
    });
    
    ret = {};
    count = 0;
    coll = $('#'+type+' tr');
    coll.each(function() {
        m = {};
        count2 = 0;
        coll2 = $(this).children('td:not(:last-child)');
        coll2.each(function() {
            item = $(this).html();
            if(item==''){ item = 'null'; }
            m[headers[count2]] = item;
            count2 += 1;
        });
        ret[count] = m;
        count += 1;
    });
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
	var strHTML = '<a href="#" onClick="saveRow(\''+id+'\',this); return false;">ok</a>&nbsp;';
	
	if( editing ) {
		strHTML += '<a href="#" onClick="cancelEdit(\''+id+'\',this); return false;">cancel</a>';
	} else {
		strHTML += '<a href="#" onClick="removeRow(\''+id+'\',this); return false;">cancel</a>';
	}
	
	return strHTML;
}

/*******************************************************************************
 * 
 * These methods are used for showing forms in each row
 * 
 *******************************************************************************/
var formShown = false;
var originalFieldValues;

// Initialize click outside of the form to close the form
$( function() {
	$( "#fade_background" ).bind( "click", function(e) {
		if( formShown != false )
			saveForm(formShown); 
	} );
});

function formKeyPress( e ) {
	if( formShown != false ) {
		if( e.which == 27 )	// Escape
			cancelForm( formShown );
		else if( e.which == 13 ) // Enter
			saveForm( formShown );
	}
}

function inputTabPress( e ) {
	if( e.which == 9 && !e.shiftKey ) {	// Tab press (without shift)
		// Show the form in the next td. If the next td contains buttons,
		// just close this form
		var td = $(e.target).parents( "td" ).first();
		var tdIndex = td.index(); 
		var nextTd = td.next();

		// If no next td is found, return
		if( nextTd.length == 0 )
			return;
		
		if( saveForm( formShown ) ) {
			// If we have saved the form for a new interaction,
			// we should open the td in the row above
			if( td.parents( ".addNew" ).length > 0 ) {
				nextTd = td.parent().prev().find( "td" ).eq( tdIndex + 1 );
			}
			
			// If the next td contains buttons, close this form and focus
			// on the first button
			if( nextTd.hasClass( "buttons" ) ) {
				$( "a", nextTd ).first().focus();
			} else {
				showForm( nextTd );
			}
			return false;
		} 
		
		return false;
	}
}

function showForm(td) {
	if( formShown ) {
		saveForm( formShown );
	}
	
	// Store fields in case we want to cancel it
	storeFields( td );
	
	$(td).addClass( "form-active" );
	
	if( !isRunningIE7OrBelow ) {
		$( "#fade_background" ).show()
	}
	
	// Set focus to the correct input field
	var form = $( ".more_inputs", $(td) );
	$( ".focus", form ).focus();
	
	// Make sure none of the fields is marked invalid
	$( "input[type=text]", form ).removeClass( "invalid" );
	
	// Make sure that a tab press on the last input will send you to the next form
	$( "input[type=text]", $(td) ).last().bind( "keydown", inputTabPress );

    // Make sure that snp_refs wil be checked
    $("input[name='genotype-snp_ref']", $(td)).bind("keyup", get_snp_url)
    
	$( document ).bind( "keyup", formKeyPress );
	formShown = td;
}

function hideForm(td) {
	// Hide the form and remove the background color
	$(td).removeClass( "form-active" );
	$( document ).unbind( "keyup", formKeyPress );
	
	// Make sure that a tab press event handler is removed
	$( "input[type=text]", $(td) ).last().unbind( "keydown", inputTabPress );
	
    // Make sure that snp_refs will not be checked anymore
    $("input[name='genotype-snp_ref']", $(td) ).unbind("keyup", get_snp_url)
	
	
	$( "#fade_background" ).hide();
}

function saveForm(td) {
    // Check form constraints and show relevant alerts
	if( checkFormConstraints( td ) ) {
		// Hide the form and store the fields
		hideForm(td);
		
		updateFields( td );
		
		// Check if this entry also exists in the interactCache list. If so
		// also update attached objects
		var tr = $(td).parents( "tr" );
		
		if( interactCache[ tr.index() ] != undefined ) {
			interactCache[ tr.index() ] = updateObjectsBasedOnInteraction( tr );
		}
		
		formShown = false;
		
		// If we are in a 'new row' and have values entered, store the row and add a new one
		var hasValues = false;
		$.each( $(td).find( "input[type=text]" ), function( idx, el ) {
			if( hasValues )
				return;
			
			if( $.trim( $(el).val() ) != "" ) 
				hasValues = true;
		});
		
		if( td.parents( ".addNew" ).length > 0 && hasValues ) {
			saveRow('interaction', td.siblings( ".buttons" ) ); 
		}
		
		return true;
	} else {
		return false;
	}
}

function cancelForm(td) {
	// Hide the form and reset the fields
	hideForm(td);
	resetFields(td);
	
	formShown = false;
}

function showFormByElement( element ) {
	showForm( $(element).parents( "td" ).first() );
}
function saveFormByElement( element ) {
	saveForm( $(element).parents( "td" ).first() );
}
function cancelFormByElement( element ) {
	cancelForm( $(element).parents( "td" ).first() );
}

function updateFields( td ) {
	var form = $( ".more_inputs", $(td) );
	
	// Update the text in the field by combining all
	// data from fields with class "label"
	var label = "";
	$( ".label", form ).each( function( idx, el ) {
		if( $(el).val() != "" )
			label += ( label == "" ? "" : ", " ) + $.trim( $(el).val() );
	});
	
	$( "input.all", $(td) ).val( label );
	$( "a.all", $(td) ).html( label );	
}

function storeFields( td ) {
	var form = $( ".more_inputs", $(td) );
	
	// Loop through all fields in the form and reset the value
	originalFieldValues = {};
	$( "input[type=text]", form ).each( function( idx, el ) {
		originalFieldValues[ $(el).attr( 'name' ) ] = $(el).val();
	});
}

function resetFields( td ) {
	var form = $( ".more_inputs", $(td) );
	
	// Loop through all fields in the form and reset the value
	$( "input[type=text]", form ).each( function( idx, el ) {
		$(el).val( originalFieldValues[ $(el).attr( 'name' ) ] );
	});
}

function updateObjectsBasedOnInteraction( row ) {
	var fieldsToUpdate = getFieldsToUpdate();
	var checkFields = {};
	
	for( type in fieldsToUpdate ) {
		checkFields[ type ] = [];
		for( i = 0; i < fieldsToUpdate[ type ].length; i++ ) {
			checkFields[ type ][ i ] = $.trim( $( fieldsToUpdate[ type ][ i ], row ).val() );
		}
	}
	
	return findOrAddMatchingObjects( checkFields );
}

function checkFormConstraints( td, show_alerts) {
	var validated = true;
	$( "input.required", $(td) ).each( function( idx, el ) {
		if( $.trim( $(el).val() ) == "" ) {
			$(el).addClass( "invalid" );
			validated = false;
		} else {
			$(el).removeClass( "invalid" );
		}
	});
    
    // Additional checks on inputs that cannot be caught with the above selector
    if($(td).find('input[id="input_gene"]').val()==''){
        if(show_alerts){
            alert("Please fill in the gene name field to continue.");
        }
        $(td).find('input[id="input_gene"]').addClass( "invalid" );
        return false;
    }
    ref = $(td).find('input[name="genotype-snp_ref"]').val();
    if(ref!=undefined){
        if(!ref.match(/^(rs)?\d{0,200}$/)){
            if(show_alerts){
                alert("Please fill in a valid SNP ref to continue.");
            }
            $(td).find('input[name="genotype-snp_ref"]').addClass( "invalid" );
            return false;
        }  
    }
    if($(td).find('input[id="input_panel_description"]').val()==''){
        if(show_alerts){
            alert("Please fill in the panel description field to continue.");
        }
        $(td).find('input[id="input_panel_description"]').addClass( "invalid" );
        return false;
    }
    if($(td).find('input[id="input_phenotype_name"]').val()==''){
        if(show_alerts){
            alert("Please fill in the phenotype name field to continue.");
        }
        $(td).find('input[id="input_phenotype_name"]').addClass( "invalid" );
        return false;
    }
    
	if( !validated ) {
        if(show_alerts){
            alert( "Please fill in all required fields." );
        }
		$( "input.invalid", $(td) ).first().focus();
	}
	
	return validated;
}

JSON.stringify = JSON.stringify || function (obj) {
    var t = typeof (obj);
    if (t != "object" || obj === null) {
        // simple data type
        if (t == "string") obj = '"'+obj+'"';
        return String(obj);
    }
    else {
        // recurse array or object
        var n, v, json = [], arr = (obj && obj.constructor == Array);
        for (n in obj) {
            v = obj[n]; t = typeof(v);
            if (t == "string") v = '"'+v+'"';
            else if (t == "object" && v !== null) v = JSON.stringify(v);
            json.push((arr ? "" : '"' + n + '":') + String(v));
        }
        return (arr ? "[" : "{") + String(json) + (arr ? "]" : "}");
    }
};

/****
 * Call the application to see if dbSNP contains a particular ref
 * Will return '' if not, and the relevant url if it does.
 ***/
function get_snp_url(e) {
    var ref = $(this).val()
    $(this).removeClass( "invalid" );
    
    // If this request is not necessary, don't do it
    if(get_snp_url_request_last_ref == ref){
        return false;
    }
    // If no ref is entered, the user isn't interested
    // Reset everything
    if(ref == '' || ref == null){
        $(this).css("backgroundImage", "None");
        get_snp_url_request.abort();
        get_snp_url_request_last_ref = ''
        return false;
    }
    
    // If the ref is nonsensical, don't look it up.
    if(!ref.match(/^(rs)?\d{0,200}$/)){
        // Not setting the inputfield to red when user has only typed 'r' or 'rs'
        if(!ref.match(/^r$/)){
            $(this).addClass( "invalid" );
        }
        $(this).css("backgroundImage", "None");
        return false;
    }    
    
    // Clear out old request.
    if(get_snp_url_request){
        get_snp_url_request.abort();
        get_snp_url_request_last_ref = ref
    }
    
    // Now build up a new request.
    var that = this
    var result_of_call = '';
    var image_to_set = '';
    var data = { ref:ref };
    var args = { type:"POST", 
                 url:"/ajax_snp/"+ref, 
                 data:data};
    get_snp_url_request = $.ajax(args)
    get_snp_url_request.done(function(result){
        result_of_call = result;
        if (result_of_call != ''){
            $(that).css("backgroundImage", "url('/static/images/icons/accept.png')");
            $(that).css("background-repeat", "no-repeat");
            $(that).css("background-position", "right top");
        } else {
            $(that).css("backgroundImage", "None");
            $(this).addClass( "invalid" );
        }
    });
    return false;
};

/**
 * Initializes autofill options for all inputs in .autofill classes within the given container
 * @param container
 */
function initAutoFill( container ) {
	if( container == undefined )
		container = $(document);
	
	// Initialize autofill lists. Each input in a .autofill element
	// will be initialized with an autocomplete. The values will be
	// the values that are given in the autofill_lists and the type
	// should be specified by the 'rel' element on the .autofill element.
	// e.g.: <div class="autofill" rel="year_of_publication"><input type="text"></div>
	$( ".autofill", container ).each( function( idx, el ) {
		var rel = $(el).attr( "rel" );
		if( rel && availableFields[ rel ] ) {
			$("input", $( el ) ).autocomplete({
				source: availableFields[ rel ]
			}).bind( "click", autoCompleteClick );
		}
	});
}

/**
 * Destroys autofill options for all inputs in .autofill classes within the given container
 * @param container
 */
function destroyAutoFill( container ) {
	if( container == undefined )
		container = $(document);
	
	// Destroy autofill lists. 
	// e.g.: <div class="autofill" rel="year_of_publication"><input type="text"></div>
	$( ".autofill", container ).each( function( idx, el ) {
		$(".ui-autocomplete-input" , $( el ) ).unbind( "click", autoCompleteClick );
		$("input", $( el ) ).autocomplete( 'destroy' );
	});
}

function autoCompleteClick(e) {
	$this = $(this);
	
	$this.blur();
    
	// pass empty string as value to search for, displaying all results
	// This only works with minLength set to zero
    var oldMinLength = $this.autocomplete( "option", "minLength" );
    $this.autocomplete( "option", "minLength", 0 );
    $this.autocomplete( "search", $this.val() );
    $this.autocomplete( "option", "minLength", oldMinLength );
    
    $this.focus();
}