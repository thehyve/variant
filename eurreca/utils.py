from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction, Link_to_dbSNP
from eurreca.forms import StudyFormSet, StudyForm, GenotypeFormSet, GenotypeForm, PhenotypeFormSet, PhenotypeForm, PanelForm, PanelFormSet, InteractionForm, InteractionFormSet
from itertools import chain
import operator, time, urllib2, sys
from django.db.models import Q
from django.shortcuts import render
from django.conf import settings
from django.core.exceptions import ValidationError

def process_clientside_studydata(jason, study, study_formset, request):
    saved_objects = {'genotype':{},'phenotype':{},'panel':{}}
    interactionValues = {}
    try:
        # Non-interaction fields first, so that all necessary primary keys can be known
        ''' 'forms' layout is as follows: 
                {
                    'genotype':
                        {
                            '0': a form, 
                            '1':, a second form, 
                            ...
                        },
                    'phenotype':
                        {
                            '0':... 
                        },
                    ...
                }
            However, the 'interaction' entry that will
            be added later, is a list...
        '''
        
        forms = add_non_interaction_forms(jason, study)
        error_messages = []
        
        for key in forms:
            for formnumber in forms[key]:
                form = forms[key][formnumber]
                if not form.is_valid():
                    error_messages.append(form.errors.items())
                else:
                    obj = form.save()    
                    # for later use in 'set_interaction_relations'
                    saved_objects[key][str(formnumber)] = obj
                
        # Interaction fields   
        
        forms['interaction'] = []
        forms = add_interaction_forms(jason, study, saved_objects, forms)
        saved_objects['interaction'] = []
        for count, form in enumerate(forms['interaction']):
            interactionValues[count] = get_interaction_values(str(count), forms, jason['interactionRelations'], form) 
        for count, form in enumerate(forms['interaction']):
            if not form.is_valid():
                error_messages.append(form.errors.items())
            else:
                obj = form.save(commit=False) 
                obj.save()
                if count < len(jason['interactionRelations']):
                    if jason['interactionRelations'].has_key(str(count)):
                        obj = set_interaction_relations(obj, saved_objects, interactionValues[count])
                    obj.save()
                    saved_objects['interaction'].append(obj)
                
        if not len(error_messages) == 0:
            raise ValidationError('Some of the forms did not validate. {0}'.format(error_messages))
            
        return forms
    except ValidationError as inst:
        print "\nin eurrecca.utils: ",inst,inst.args
        exception = []
        if forms.has_key('interaction'):
            print '\n\ninteraction key found\n\n'
            exception = [inst,
                {'formset' : study_formset, 
                'formsetGenotype' : forms['genotype'],
                'formsetPhenotype' :  forms['phenotype'],
                'formsetPanel' :  forms['panel'],
                'formsetInteraction' :  forms['interaction'],
                'interactionValues' : interactionValues}]
        else:
            print '\n\nNO interaction key found\n\n'
            exception = [inst,
                {'formset' : study_formset, 
                'formsetGenotype' : forms['genotype'],
                'formsetPhenotype' :  forms['phenotype'],
                'formsetPanel' :  forms['panel']}]
        raise ValidationError(exception)
        
def set_interaction_relations(obj, saved_objects, interactionValuesMap):
    # At this moment in time we are not yet dealing with lists, but single items
    if interactionValuesMap['interactCache'].has_key('genotype'):
        obj.genotypes.add(saved_objects['genotype'][interactionValuesMap['interactCache']['genotype']])
    if interactionValuesMap['interactCache'].has_key('phenotype'):
        obj.phenotypes.add(saved_objects['phenotype'][interactionValuesMap['interactCache']['phenotype']])
    if interactionValuesMap['interactCache'].has_key('panel'):
        obj.panels.add(saved_objects['panel'][interactionValuesMap['interactCache']['panel']])
    return obj

def get_interaction_values(idx, forms, relations_lists, form):
    # At this moment in time we are not yet dealing with lists, but single items
    relations_list = []
    return_map = {}
    return_map['interactCache'] = {}
    if relations_lists.has_key(str(idx)):
        relations_list = relations_lists[str(idx)]
        if not relations_list['genotype'] == -1:
            index = str(relations_list['genotype'])
            return_map['interactCache']['genotype'] = index
            return_map['gene'] = forms['genotype'][index].data['gene']
            return_map['snp_ref'] = forms['genotype'][index].data['snp_ref']
            return_map['snp_variant'] = forms['genotype'][index].data[
                'snp_variant']
        if not relations_list['phenotype'] == -1:
            index = str(relations_list['phenotype'])
            return_map['interactCache']['phenotype'] = index
            return_map['phenotype_name'] = forms['phenotype'][index].data[
                'phenotype_name']
        if not relations_list['panel'] == -1:
            index = str(relations_list['panel'])
            return_map['interactCache']['panel'] = index
            return_map['panel_description'] = forms['panel'][index].data[
                'panel_description']
                
    # Set regular interaction fields, even if it has no relations
    for field in form:
        if (field.name=='genotypes' or field.name=='phenotypes' or field.name=='panels' or
            field.name=='id'):
            continue
        else:
            return_map[field] = field.value()
    return return_map
    
def add_non_interaction_forms(jason, study):
    # Fully functional
    forms = {'genotype':{},'phenotype':{},'panel':{}}
    count = sys.maxint
    for key1 in jason:
        if not forms.has_key(key1):
            # 'interaction' key is not yet present at this point
            continue
        for key2 in jason[key1]:
            form = None
            if key1 == 'genotype': 
                form = GenotypeForm(Genotype.objects.none())
            if key1 == 'phenotype':
                form = PhenotypeForm(Phenotype.objects.none())
            if key1 == 'panel':
                form = PanelForm(Panel.objects.none())
            if not form == None:
                form.data['study'] = study.id
                for field in form:
                    if jason[key1][key2].has_key(field.name):
                        form.data[field.name] = jason[key1][key2][field.name]
                        if form.data[field.name] == 'null':
                            form.data[field.name] = None
                forms[key1][key2] = form
            count -= 1
    return forms
    
def add_interaction_forms(jason, study, saved_objects, forms):
    # Does not set all fields yet
    forms['interaction'] = []
    keylist = jason['interaction'].keys()
    keylist.sort()
    for key1 in keylist:
        form = InteractionForm(Interaction.objects.none())
        form.data['study'] = study.id
        for field in form:
            if (field.name == 'genotypes' or field.name == 'phenotypes' 
                or field.name == 'panels'):
                continue
            if jason['interaction'][key1].has_key(field.name):
                form.data[field.name] = jason['interaction'][key1][field.name]
                if form.data[field.name] == 'null':
                    form.data[field.name] = None
        forms['interaction'].append(form) 
    return forms
    
def errors_to_string(errors):
    returnMessage = ''
    for item in errors:
        returnMessage += "Field '"+item[0]+"': "
        for error in item[1]:
            returnMessage += error+" "
        returnMessage += ' '    
    return returnMessage

def get_interactionValues_from_formsets(fs):
    ''' Return variable is formatted as follows:
        { 
            interaction id : {
                field       : value,
                other field : other value,
                ... : ...,
                interactCache : {
                    'panels'        : value,
                    'phenotypes'    : value,
                    'genotypes'     : value
                }
            }
        }
    
    '''
    interactionValues = {}
    for form in fs['interaction']:    
        id = form['id'].value()
        interactionValues[id] = {}
        interactionValues[id]['interactCache'] = {}
        for field in form:
            if field.name=='genotypes' or field.name=='phenotypes' or field.name=='panels':
                for f in fs['genotype']:
                    if len(form['genotypes'].value()) > 0 and f['id'].value() == form['genotypes'].value()[0]:
                        interactionValues[id]['interactCache'][
                            'genotypes'] = f['id'].value()
                        interactionValues[id]['gene'] = f['gene'].value()
                        interactionValues[id][
                            'snp_ref'] = f['snp_ref'].value()
                        interactionValues[id][
                            'snp_variant'] = f['snp_variant'].value()
                        break
                for f in fs['phenotype']:
                    if len(form['phenotypes'].value()) > 0 and f['id'].value() == form['phenotypes'].value()[0]:
                        interactionValues[id]['interactCache'][
                            'phenotypes'] = f['id'].value()
                        interactionValues[id][
                            'phenotype_name'] = f['phenotype_name'].value()
                        break
                for f in fs['panel']:
                    if len(form['panels'].value()) > 0 and f['id'].value() == form['panels'].value()[0]:
                        interactionValues[id]['interactCache'][
                            'panels'] = f['id'].value()
                        interactionValues[id][
                            'panel_description'] = f['panel_description'].value()
                        break
            if field.name=='id':
                continue
            else:
                interactionValues[id][field.name] = field.value()
    
    return interactionValues
    
def get_formset_maps_by_id(id):
    ''' Return variable layout is as follows: 
            {
                'genotype':
                    {
                        '0': a form, 
                        '1':, a second form, 
                        ...
                    },
                'phenotype':
                    {
                        '0':...,
                        ...
                    },
                'panel':
                    {
                        '0':...,
                        ...
                    },
                'interaction': [form, different form]
                'study': [study form]
            }
    '''
    '''formSets = {'study':formset,'genotype':formsetGenotype,
        'phenotype':formsetPhenotype,'panel':formsetPanel,
        'interaction':formsetInteraction}
        '''
    returnFormSets = {'study':[],'genotype':{},
        'phenotype':{},'panel':{},
        'interaction':[]}
    inputFormSets = get_formsets_by_id(id)
    for index, form in enumerate(inputFormSets['genotype']):
        returnFormSets['genotype'][index] = form
    for index, form in enumerate(inputFormSets['phenotype']):
        returnFormSets['phenotype'][index] = form
    for index, form in enumerate(inputFormSets['panel']):
        returnFormSets['panel'][index] = form
    returnFormSets['study'] =  inputFormSets['study']
    returnFormSets['interaction'] =  inputFormSets['interaction']
    return returnFormSets    

def get_formsets_by_id(id):
    qs = Study.objects.filter(pk=id)     
    formset = []
    key = id
    if not len(qs) == 0:
        formset = StudyFormSet(
            queryset=qs,
            prefix="study")
        
    qs = Genotype.objects.filter(study=key).order_by('id')       
    formsetGenotype = []
    if not len(qs) == 0:
        formsetGenotype = GenotypeFormSet(
            queryset=qs, 
            prefix="genotype")
    
    qs = Phenotype.objects.filter(study=key).order_by('id')       
    formsetPhenotype = []
    if not len(qs) == 0:
        formsetPhenotype = PhenotypeFormSet(
            queryset=qs, 
            prefix="phenotype")
        
    qs = Panel.objects.filter(study=key).order_by('id')    
    formsetPanel = []
    if not len(qs) == 0:
        formsetPanel = PanelFormSet(
            queryset=qs, 
            prefix="panel")
        
    qs = Interaction.objects.filter(study=key).order_by('id')   
    formsetInteraction = []
    if not len(qs) == 0:
        formsetInteraction = InteractionFormSet(
            queryset=qs, 
            prefix="interaction")
        
    formSets = {'study':formset,'genotype':formsetGenotype,
        'phenotype':formsetPhenotype,'panel':formsetPanel,
        'interaction':formsetInteraction}
    return formSets
    
def get_formsets_from_model_objects(list):
    # Does not return empty formsets
    q_objects = {'genotype':[],'phenotype':[],'panel':[],'study':[],
        'interaction':[]}
    for item in list:
        t = type(item)
        if t == Interaction:
            q_objects['interaction'].append(Q(pk=item.id))
            continue    
        if t == Phenotype:
            q_objects['phenotype'].append(Q(pk=item.id))
            continue
        if t == Panel:
            q_objects['panel'].append(Q(pk=item.id))
            continue
        if t == Genotype:
            q_objects['genotype'].append(Q(pk=item.id))
            continue
        if t == Study:    
            q_objects['study'].append(Q(pk=item.id))
            continue
            
    formSets = get_formsets_from_q_objects(q_objects)    
    return formSets
    
def get_formsets_from_q_objects(q_objects):
    formSets_0 = {'genotype':None,'phenotype':None,'panel':None,'study':None,
        'interaction':None}     
        
    for key in formSets_0:
        filter = None
        if len(q_objects[key]) == 0:
            continue
        else:
            filter = reduce(operator.or_, q_objects[key])
            if key == 'study':        
                q = Study.objects.filter(filter)
                if q:
                    formSets_0[key] = StudyFormSet(
                        queryset=q, 
                        prefix=key)
                continue    
            if key == 'genotype':        
                q = Genotype.objects.filter(filter)
                if q:
                    formSets_0[key] = GenotypeFormSet(
                        queryset=q, 
                        prefix=key)
                continue
            if key == 'phenotype':     
                q = Phenotype.objects.filter(filter)
                if q:
                    formSets_0[key] = PhenotypeFormSet(
                        queryset=q, 
                        prefix=key)
                continue
            if key == 'panel':
                q = Panel.objects.filter(filter)
                if q:
                    formSets_0[key] = PanelFormSet(
                        queryset=q, 
                        prefix=key)
                continue
            if key == 'interaction':        
                q = Interaction.objects.filter(filter)
                if q:
                    formSets_0[key] = InteractionFormSet(
                        queryset=q, 
                        prefix=key)
                continue
    # Return non-empty formsets
    formSets_1 = {'genotype':None,'phenotype':None,'panel':None,'study':None,
        'interaction':None}     
    for key in formSets_1:
        if not formSets_0[key] == None:
            if len(formSets_0[key])>0:
                formSets_1[key] = formSets_0[key]
    return formSets_1
    
def get_model_from_search_term(field_name):
    from_term_to_model_type = {
        "Study id":"study",
        "Pubmed id":"study",
        "Year of publication":"study",
        "Micronutrient":"study",
        "Gene":"genotype",
        "SNP ref":"genotype",
        "Phenotype name":"phenotype",
        "SNP variant":"genotype"
    }
    return from_term_to_model_type[field_name]
    

def get_field_from_search_term(field_name):
    from_string_to_proper_field_name = {
        "Study id":"study",
        "Pubmed id":"pubmed_id",
        "Year of publication":"year_of_publication",
        "Micronutrient":"micronutrient",
        "Gene":"gene",
        "SNP ref":"snp_ref",
        "Phenotype name":"phenotype_name",
        "SNP variant":"snp_variant"
    }
    return from_string_to_proper_field_name[field_name]
    
def get_year_list():
    ''' Returns a list containing, in integer form, each year from 
        the year now+1 to the year now-year_list_length+1 '''
    year_list_length = 60
    try: # Try to find ovverriding settings
        year_list_length = settings.YEAR_LIST_LENGTH
    except Exception:
        year_list_length = 60
    year_list = []
    now = time.localtime()
    for n in range(year_list_length): 
        year_list.append(now.tm_year - n + 1)
    return year_list    
    
def get_autofill_lists():
    ''' Returns a dict containing lists of field contents that 
        can be used for autofill purposes.
        Will return lists for the following field names:

        micronutrient (from study database objects)
        endpoint (from study)
        journal_title (from study)
        study_type (from study)
        environmental_factor (from study)
        gene (gene name, used in both genotype and interaction tables, 
                from genotype)
        phenotype_name (used in both phenotype and interaction tables, 
                from phenotype)
        statistical_model (from interaction)
        year_of_publication ( see get_year_list/1 )
    '''
    lists = {
        'micronutrient':[],
         'endpoint':[],
         'journal_title':[],
         'study_type':[],
         'environmental_factor':[],
         'gene':[],
         'phenotype_name':[],
         'statistical_model':[]
    }
    # micronutrient, endpoint, journal_title, study_type, environmental_factor
    temp_list = Study.objects.raw('''SELECT id, micronutrient, endpoint, 
                                     journal_title, study_type, 
                                     environmental_factor FROM eurreca_study''')
    for entry in temp_list:
        lists['micronutrient'].append(entry.micronutrient)
        lists['endpoint'].append(entry.endpoint)
        lists['journal_title'].append(entry.journal_title)
        lists['study_type'].append(entry.study_type)
        lists['environmental_factor'].append(entry.environmental_factor)
    
    # gene
    temp_list = Genotype.objects.raw('''SELECT id, gene 
                                        FROM eurreca_genotype''')
    for entry in temp_list:
        lists['gene'].append(entry.gene)
    
    # phenotype_name
    temp_list = Phenotype.objects.raw('''SELECT id, phenotype_name 
                                         FROM eurreca_phenotype''')
    for entry in temp_list:
        lists['phenotype_name'].append(entry.phenotype_name)
    
    # statistical_model
    temp_list = Interaction.objects.raw('''SELECT id, statistical_model 
                                         FROM eurreca_interaction''')
    for entry in temp_list:
        lists['statistical_model'].append(entry.statistical_model)
    
    # Removing duplicate and empty list items
    for key in lists:
        lists[key] = clean_list(list(set(lists[key])), ['', 'None', None])
    
    # Add year list    
    lists['year_of_publication'] = get_year_list()
    
    return lists

def clean_list(list, dirty_bits = []):
    ''' Returns it's list argument cleaned of 'None's, or cleaned of whichever
        items were listed in 'dirty_bits'.
    '''
    if dirty_bits == []:
        return [item for item in list if item != None]
    else:
        return [item for item in list if not item in dirty_bits]
        
def substract_list_from_list(list1, list2):
    ''' Returns a new list that contains all the items in list1 that are not
        present in list2
    '''
    return [a for a in list1 if not a in list2]
    
def call_entrez(snp_ref):
    if snp_ref.startswith('rs'):
        snp_ref = snp_ref.strip('rs')
    search_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=snp&id={0}&report=GENB'.format(snp_ref)
    requested_url = 'http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?searchType=adhoc_search&type=rs&rs=rs{0}'.format(snp_ref)
    error = False
    error_code = ''
    try:
        try:
            fileHandle = urllib2.urlopen(search_url)
            fileHandle.close()
        except urllib2.HTTPError, e:
            error = True
            error_code = e.code
    except IOError:
        #print 'Cannot open URL %s for reading' % search_url
        str1 = 'error!'
        return {'message': 'dbSNP Entrez service appears to be unavailable.', 'messageType': 'negative'}
    if error:
        #print 'Error occurred:', error_code
        if error_code==400:
            return {'message': 'No such snp ref could be found in dbSNP.', 'messageType': 'negative'}
        else:
            return {'message': 'dbSNP Entrez service appears to be unavailable.', 'messageType': 'negative'}
    else:
        #print 'search succesful'
        l = Link_to_dbSNP(snp_ref=snp_ref, url=requested_url)
        l.save()
        return {'message': 'Requested URL: <a href="{0}">{0}</a>'.format(requested_url), 'messageType': 'positive'}
        
def get_list_of_snp_refs_from_formsets(fs):
    list_of_snp_refs = []
    for f in fs['genotype']:
        list_of_snp_refs.append(f['snp_ref'].value())
    return list_of_snp_refs
        
def get_snp_ref_to_dbSNP_url_dict(list_of_snp_refs):
    #print 'get_snp_ref_to_dbSNP_url_dict:',list_of_snp_refs
    if list_of_snp_refs == []:
        return {}
    q = []
    for ref in list_of_snp_refs:
        if ref == None or ref == '':
            continue
        if ref.startswith('rs'):
           ref = ref.strip('rs')
        #print 'about to look for ref',ref
        q.append(Q(snp_ref = ref))
    if q == []:
        return {}
    filter = reduce(operator.or_, q)    
    #print filter
    items = Link_to_dbSNP.objects.filter(filter)
    results = {}
    for item in items:
        results[item.snp_ref] = item.url
    return results
    
def get_Link_to_dbSNP_by_ref(ref):
    if ref == None or ref == '':
        return None
    if ref.startswith('rs'):
       ref = ref.strip('rs')
    link = None
    try:
        link = Link_to_dbSNP.objects.get(snp_ref=ref)
        return link
    except:
        return None
        
def get_mouseover_text():
    mouseover_text = {}
    mouseover_text["significant_associations"] = "Record details of any statistically significant associations or interactions between genotype and either diet, status, environmental factors or health outcomes reported in the study."
    mouseover_text["ratio_type"]  = "Select whether the paper reports hazard ratios (HR), odds ratios (OR) or relative risk (RR)."
    mouseover_text["ci_lower"] = "Enter the lower end 95% CI (confidence interval) for either the HR, OR or RR reported previously."
    mouseover_text["ci_upper"] = "Enter the upper end 95% CI (confidence interval) for either the HR, OR or RR reported previously."
    mouseover_text["p_value"] = "Enter the p-value for interaction for the previously reported HR, OR or RR.";
    mouseover_text["p_value_for_trend"] = "Enter the p-value for trend (statistical significance) for the previously reported HR, OR or RR."
    mouseover_text["statistical_model"] = "Enter information on the statistical model used to evaluate the data. Note: the paper may report the use of more than one statistical approach e.g. a different model may be used to evaluate 'trends' as opposed to 'interactions'."
    mouseover_text["gene"] = "Enter the commonly used name for the gene e.g. MTHFR, HFE"
    mouseover_text["snp_ref"] = "Enter the SNP reference number, IDs beginning with rs are SNPs from the NCBI SNPs database. If you enter a new SNP reference number and this field gets a green icon, the SNP has been found in the NCBI SNPs database."
    mouseover_text["snp_variant"] = "Enter details of the SNP variant where provided e.g. AA, TT or AT."
    mouseover_text["snp_name"] = "Enter the SNP name. In addition to the SNP reference (accession) number or HGVS number, papers sometimes report a SNP name which may provide information on the location of the SNP in relation to the gene. The SNP name is sometimes reported concatenated with the gene name e.g. MAT1A_d18777."
    mouseover_text["phenotype_name"] = "Describe the relevant phenotype or biomarkers of status reported. Examples of phenotype include BMI, bone density."
    mouseover_text["intake_data"] = "Enter details of the dietary micronutrient intake if reported. This may be reported as supplemental micronutrient, habitual intake, or both."
    mouseover_text["environmental_factor"] = "Enter details of any relevant environmental factor e.g. habitual dietary intake, status, physical activity, smoking etc."
    mouseover_text["comments"] = "Enter details of potentially useful information related to the paper or the reported study which has not been captured elsewhere."
    mouseover_text["study_type"] = "Select the type of study e.g. nested case control, prospective cohort etc. from the list. Where the design is unusual or not listed, please include a description in the comments field."
    mouseover_text["number_of_participants"] = ""
    mouseover_text["journal_title"] = "Enter the title of the journal"
    mouseover_text["paper_title"] = "Enter the full title of the paper."
    mouseover_text["endpoint"] = "Enter details of the health outcome which is linked to the SNP under investigation e.g. stroke, coronary heart disease etc."
    mouseover_text["gender"] = ""
    mouseover_text["population"] = "Enter details of the population group e.g. where the study was undertaken etc. and provide numbers of cases and controls as appropriate e.g. US PHS study; healthy US physicians (cases:1286; controls: 1267)."
    mouseover_text["micronutrient"] = "List the EURRECA priority micronutrient for which the paper is relevant; separate micronutrients with a comma where the paper is relevant to more than one: folate, B12"
    mouseover_text["authors"] = "Enter details of the authors of the paper, but limit names to the first three authors."
    mouseover_text["year_of_publication"] = "Enter the year of publication of the paper."
    mouseover_text["study_id"] = "Add the first author and year, as detailed in the following example Smith1999"
    mouseover_text["allele"] = ""
    mouseover_text["mutation"] = ""
    mouseover_text["zygosity"] = ""
    mouseover_text["number_of_people_with_genotype"] = ""
    mouseover_text["genotype_frequency"] = ""
    mouseover_text["estimated_overal_frequency"] = ""
    mouseover_text["genotype_details"] = ""
    mouseover_text["pubmed_id"] = ""
    return mouseover_text