from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction
from eurreca.forms import StudyFormSet, StudyForm, GenotypeFormSet, GenotypeForm, PhenotypeFormSet, PhenotypeForm, PanelForm, PanelFormSet, InteractionForm, InteractionFormSet
from itertools import chain
import operator
from django.db.models import Q

def hello():
    print "Oh hai there."
    
def process_clientside_studydata(jason, study, old_items):
    saved_objects = {'genotype':[],'phenotype':[],'panel':[]}
    try:
        # Non-interaction fields first, so that all necessary primary keys can be known
        forms = add_non_interaction_forms(jason, study.id)
        
        for key in forms:
            for form in forms[key]:
                if not form.is_valid():
                    print 'Encountered invalid non-interaction form'
                    print "errors:",form.errors.items()
                    raise ValueError('Some of the forms did not validate. '+errors_to_string(form.errors.items()))
        for key in forms:
            for form in forms[key]: 
                obj = form.save()    
                saved_objects[key].append(obj)
                
        # Interaction fields
        forms = add_interaction_forms(jason, study.id, saved_objects, forms)
        saved_objects['interaction'] = []
        for form in forms['interaction']:
            if not form.is_valid():
                print 'Encountered invalid interaction form'
                print "errors:",form.errors.items()
                raise ValueError('Some of the forms did not validate. '+errors_to_string(form.errors.items()))
        count = 0
        for form in forms['interaction']:
            obj = form.save(commit=False) 
            obj.save()
            obj = set_interaction_relations(obj, saved_objects, jason['interactionRelations'][str(count)])
            obj.save()
            count += 1
            saved_objects['interaction'].append(obj)
        
        return forms
    except Exception as inst:
        print "in eurrecca.utils: ",inst
        # Remove the new items and re-save the old items
        for key in saved_objects:
            for obj in saved_objects[key]:
                obj.delete()
        for key in old_items:
            for obj in old_items[key]:
                obj.save()
        raise Exception(inst)
         
def set_interaction_relations(obj, saved_objects, relations_lists):
    # At this moment in time we are not yet dealing with lists, but single items
    ''' When dealing with lists it should probably be done like this:
    for gt in relations_lists['genotype']:
        interaction.genotypes.add(saved_objects['genotype'][gt])
    '''
    obj.genotypes.add(saved_objects['genotype'][relations_lists['genotype']])
    obj.phenotypes.add(saved_objects['phenotype'][relations_lists['phenotype']])
    obj.panels.add(saved_objects['panel'][relations_lists['panel']])
    return obj
    
def add_non_interaction_forms(jason, id):
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
                form.data['study_id'] = id
                for field in form:
                    if jason[key1][key2].has_key(field.name):
                        form.data[field.name] = jason[key1][key2][field.name]
                        if form.data[field.name] == 'null':
                            form.data[field.name] = None
                forms[key1].append(form)
    return forms
    
def add_interaction_forms(jason, study_id, saved_objects, forms):
    # Does not set all fields yet
    forms['interaction'] = []
    for key1 in jason['interaction']:
        interactionData = jason['interaction'][key1]
        form = InteractionForm(Interaction.objects.none())
        form.data['study_id'] = study_id
        for field in form:
            if field.name == 'ratio':
                form.data[field.name] = jason['interaction'][key1]
            if field.name == 'genotypes' or field.name == 'phenotypes' or field.name == 'panels':
                continue
        forms['interaction'].append(form)         
    return forms
    
def errors_to_string(errors):
    returnMessage = ''
    for item in errors:
        print 'item',item[0],item.__class__()
        returnMessage += "Field '"+item[0]+"': "
        for error in item[1]:
            print '\terror',error,error.__class__()
            returnMessage += error+" "
        returnMessage += ' '    
    return returnMessage
    
def get_formsets_by_id(id):
    formset = StudyFormSet(
        queryset=Study.objects.filter(pk=id), 
        prefix="study")
    formsetGenotype = GenotypeFormSet(
        queryset=Genotype.objects.filter(study_id=id), 
        prefix="genotype")
    formsetPhenotype = PhenotypeFormSet(
        queryset=Phenotype.objects.filter(study_id=id), 
        prefix="phenotype")
    formsetPanel = PanelFormSet(
        queryset=Panel.objects.filter(study_id=id), 
        prefix="panel")
    formsetInteraction = InteractionFormSet(
        queryset=Interaction.objects.filter(study_id=id), 
        prefix="interaction")
    formSets = {'study':formset,'genotype':formsetGenotype,
        'phenotype':formsetPhenotype,'panel':formsetPanel,
        'interaction':formsetInteraction}
    return formSets
    
def get_formsets_from_model_objects(list):
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
    formSets = {'genotype':None,'phenotype':None,'panel':None,'study':None,
        'interaction':None}     
    for key in formSets:
        if len(q_objects[key]) == 0:
            continue
        else:
            filter = reduce(operator.or_, q_objects[key])
            if key == 'study':        
                q = Study.objects.filter(filter)
                if q:
                    formSets[key] = StudyFormSet(
                        queryset=q, 
                        prefix=key)
                continue    
            if key == 'genotype':        
                q = Genotype.objects.filter(filter)
                if q:
                    formSets[key] = GenotypeFormSet(
                        queryset=q, 
                        prefix=key)
                continue
            if key == 'phenotype':     
                q = Phenotype.objects.filter(filter)
                if q:
                    formSets[key] = PhenotypeFormSet(
                        queryset=q, 
                        prefix=key)
                continue
            if key == 'panel':
                q = Panel.objects.filter(filter)
                if q:
                    formSets[key] = PanelFormSet(
                        queryset=q, 
                        prefix=key)
                continue
            if key == 'interaction':        
                q = Interaction.objects.filter(filter)
                if q:
                    formSets[key] = InteractionFormSet(
                        queryset=q, 
                        prefix=key)
                continue
    
    return formSets