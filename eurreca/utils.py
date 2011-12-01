from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction, Link_to_dbSNP
from eurreca.forms import StudyFormSet, StudyForm, GenotypeFormSet, GenotypeForm, PhenotypeFormSet, PhenotypeForm, PanelForm, PanelFormSet, InteractionForm, InteractionFormSet
from itertools import chain
import operator, time, urllib2, sys
from django.db.models import Q
from django.shortcuts import render
from django.conf import settings

def process_clientside_studydata(jason, study, study_formset, request):
    saved_objects = {'genotype':[],'phenotype':[],'panel':[]}
    interactionValues = {}
    try:
        # Non-interaction fields first, so that all necessary primary keys can be known
        forms = add_non_interaction_forms(jason, study)
        error_messages = []
        for key in forms:
            for form in forms[key]:
                if not form.is_valid():
                    error_messages.append(form.errors.items())
                else:
                    obj = form.save()    
                    saved_objects[key].append(obj)
                
        # Interaction fields            
        forms['interaction'] = []
        forms = add_interaction_forms(jason, study, saved_objects, forms)
        saved_objects['interaction'] = []
        count = sys.maxint
        for form in forms['interaction']:
            idx = form.data['id']
            if idx != None and idx != '' and idx != Undefined:
                idx = count
            if jason['interactionRelations'].has_key(idx):
                interactionValues[idx] = get_interaction_values(idx, forms, jason['interactionRelations'][idx]) 
            count -= 1
        count = sys.maxint
        for form in forms['interaction']:
            idx = form.data['id']
            if idx != None and idx != '' and idx != Undefined:
                idx = count
            if not form.is_valid():
                error_messages.append(form.errors.items())
            else:
                obj = form.save(commit=False) 
                obj.save()
                if count < len(jason['interactionRelations']):
                    if jason['interactionRelations'].has_key(idx):
                        obj = set_interaction_relations(obj, saved_objects, jason['interactionRelations'][idx])
                    obj.save()
                    saved_objects['interaction'].append(obj)
                count -= 1
                
        if not len(error_messages) == 0:
            raise ValueError('Some of the forms did not validate. {0}'.format(error_messages))
            
        return forms
    except Exception as inst:
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
        raise Exception(exception)
         
def set_interaction_relations(obj, saved_objects, relations_list):
    # At this moment in time we are not yet dealing with lists, but single items
    if not relations_list['genotype'] == -1:
        obj.genotypes.add(saved_objects['genotype'][relations_list['genotype']])
    if not relations_list['phenotype'] == -1:
        obj.phenotypes.add(saved_objects['phenotype'][relations_list['phenotype']])
    if not relations_list['panel'] == -1:
        obj.panels.add(saved_objects['panel'][relations_list['panel']])
    return obj

def get_interaction_values(idx, forms, relations_list):
    # At this moment in time we are not yet dealing with lists, but single items
    return_map = {}
    if not relations_list['genotype'] == -1:
        return_map['gene'] = forms['genotype'][relations_list['genotype']].data['gene']
        return_map['snp_ref'] = forms['genotype'][relations_list['genotype']].data['snp_ref']
        return_map['snp_variant'] = forms['genotype'][relations_list['genotype']].data['snp_variant']
    if not relations_list['phenotype'] == -1:
        return_map['phenotype_name'] = forms['phenotype'][relations_list['phenotype']].data['phenotype_name']
    if not relations_list['panel'] == -1:
        return_map['panel_description'] = forms['panel'][relations_list[
            'panel']].data['panel_description']
            
    for form in fs['interaction']:
        for field in form:
            if field=='genotypes' or field=='phenotypes' or field=='panels': or
                field=='id':
                continue
            else:
                return_map[field] = form[field].value()  
                
    return return_map
    
def add_non_interaction_forms(jason, study):
    # Fully functional
    forms = {'genotype':[],'phenotype':[],'panel':[]}
    for key1 in jason:
        if not forms.has_key(key1):
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
                forms[key1].append(form)
    return forms
    
def add_interaction_forms(jason, study, saved_objects, forms):
    # Does not set all fields yet
    forms['interaction'] = []
    for key1 in jason['interaction']:
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
    interactionValues = {}
    for form in fs['interaction']:
        id = form['id'].value()
        interactionValues[id] = {}
        for field in form:
            if field=='genotypes' or field=='phenotypes' or field=='panels':
                for f in fs['genotype']:
                    if len(form['genotypes'].value()) > 0 and f['id'].value() == form['genotypes'].value()[0]:
                        interactionValues[id]['gene'] = f['gene'].value()
                        interactionValues[id][
                            'snp_ref'] = f['snp_ref'].value()
                        interactionValues[id][
                            'snp_variant'] = f['snp_variant'].value()
                        break
                for f in fs['phenotype']:
                    if len(form['phenotypes'].value()) > 0 and f['id'].value() == form['phenotypes'].value()[0]:
                        interactionValues[id][
                            'phenotype_name'] = f['phenotype_name'].value()
                        break
                for f in fs['panel']:
                    if len(form['panels'].value()) > 0 and f['id'].value() == form['panels'].value()[0]:
                        interactionValues[id][
                            'panel_description'] = f['panel_description'].value()
                        break
            if field=='id':
                continue
            else:
                interactionValues[id][field] = form[field].value()
    return interactionValues
        
    

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
    #479341
    str1 = 'Nothing happened'
    error = False
    error_code = ''
    try:
        try:
            fileHandle = urllib2.urlopen(search_url)
            str1 = fileHandle.read()
            fileHandle.close()
        except urllib2.HTTPError, e:
            error = True
            error_code = e.code
            print e.code
            print e.read()
    except IOError:
        print 'Cannot open URL %s for reading' % search_url
        str1 = 'error!'
        return {'message': 'dbSNP Entrez service appears to be unavailable.', 'messageType': 'negative'}
    #print str1    
    if error:
        print 'Error occurred:', error_code
        if error_code==400:
            return {'message': 'No such snp ref could be found in dbSNP.', 'messageType': 'negative'}
        else:
            return {'message': 'dbSNP Entrez service appears to be unavailable.', 'messageType': 'negative'}
    else:
        print 'search succesful'
        l = Link_to_dbSNP(snp_ref=snp_ref, url=requested_url)
        l.save()
        return {'message': 'Requested URL: <a href="{0}">{0}</a>'.format(requested_url), 'messageType': 'positive'}
        
def get_list_of_snp_refs_from_formsets(fs):
    list_of_snp_refs = []
    for f in fs['genotype']:
        list_of_snp_refs.append(f['snp_ref'].value())
    return list_of_snp_refs
        
def get_snp_ref_to_dbSNP_url_dict(list_of_snp_refs):
    print 'get_snp_ref_to_dbSNP_url_dict:',list_of_snp_refs
    if list_of_snp_refs == []:
        return {}
    q = []
    for ref in list_of_snp_refs:
        if ref.startswith('rs'):
           ref = ref.strip('rs')
        print 'about to look for ref',ref
        q.append(Q(snp_ref = ref))
    if q == []:
        return {}
    filter = reduce(operator.or_, q)    
    print filter
    items = Link_to_dbSNP.objects.filter(filter)
    results = {}
    for item in items:
        results[item.snp_ref] = item.url
    return results