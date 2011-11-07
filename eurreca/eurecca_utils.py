from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction
from eurreca.forms import StudyFormSet, StudyForm, GenotypeFormSet, GenotypeForm, PhenotypeFormSet, PhenotypeForm, PanelForm, PanelFormSet, InteractionForm, InteractionFormSet

def hello():
    print "Oh hai there."

    
def process_clientside_studydata(jason, study):
   
    # Non-interaction fields first, so that all necessary primary keys can be known
    forms = add_non_interaction_forms(jason, study.id)
    
    for key in forms:
        for form in forms[key]:
            if not form.is_valid():
                print "ValueError?"
                raise ValueError('Some of the forms did not validate.')
    saved_objects = {'genotype':[],'phenotype':[],'panel':[]}
    for key in forms:
        for form in forms[key]: 
            obj = form.save()    
            saved_objects[key].append(obj)
    print 'saved_objects:',saved_objects
    
    print '\ninteractions:'
    # Interaction fields
    forms = add_interaction_forms(jason, study.id, saved_objects)
    
    return forms

    
def add_non_interaction_forms(jason, id):
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
                        print key1,"     ",form.data[field.name]
                forms[key1].append(form)
    return forms
    
def add_interaction_forms(jason, study_id, saved_objects):
    forms = {}
    forms['interaction'] = []
    for key1 in jason['interaction']:
        interactionData = jason['interaction'][key1]
        form = InteractionForm(Interaction.objects.none())
        form.data['study_id'] = study_id
        #interaction_relations = retrieve_interaction_relations(jason['interactionRelations'][key1], saved_objects)
        form = interaction_relations(form, saved_objects, jason['interactionRelations'][key1])
        for field in form:
            #list = [t.pk for t in teleconference.bans.all()]
            if field.name == 'ratio':
                form.data[field.name] = jason['interaction'][key1]
            if field.name == 'genotypes' or field.name == 'phenotypes' or field.name == 'panels':
                continue
            if form.data.has_key(field.name):
                print field.name,":",form.data[field.name]        
            forms['interaction'].append(form)         
    return forms
    
def interaction_relations(form, saved_objects, relations_lists):
    #print 'relations_lists',relations_lists
    #print 'saved_objects',saved_objects
    keys = ['genotype','phenotype','panel']
    for key in keys:
        key2 = key+'s'
        print '\t 0',form.data
        print '\t 1',form.data[key2]
        print '\t 2',saved_objects[key]
        print '\t 3',relations_lists[key]
        print '\t 4',saved_objects[key][relations_lists[key]]
        form.data[key2].append(saved_objects[key][relations_lists[key]])
    return form
    
def retrieve_interaction_relations(map, saved_objects):
    data = {'genotype':[],'phenotype':[],'panel':[]}
    for key in data:
        # Currently we expect only one GT, PT or panel!
        data[key].append(saved_objects[key][map[key]])
    return data
        
def retrieve_interaction_items(jason, forms, key1, key2):
    hello()
    '''# Determine which items are presend in this interaction,
    # and extract their values
    datas = {'genotype':{},'phenotype':{},'panel':{}}
    form_numbers = {'genotype':[],'phenotype':[],'panel':[]}
    print 'Determine which items are present in this interaction'
    for entry in jason[key1][key2]:
        labels = entry.split('-')
        if len(labels) > 1:
            if datas.has_key(labels[0]):
                # One of the valid domain types
                if not datas[labels[0]].has_key(labels[1]):
                    datas[labels[0]][labels[1]] = {}
                if not datas[labels[0]][labels[1]].has_key(labels[2]):
                    datas[labels[0]][labels[1]][labels[2]] = {}
                datas[labels[0]][labels[1]][labels[2]] = jason[key1][key2][entry]
                exists = True
                #print labels[0],labels[1],datas[labels[0]][labels[1]]
                for key3 jason[labels[0]]:
                    if not jason[labels[0]][key3].has_key():
                        exists = False
    print 'TODO: The follwoing items should be added to this interaction::',form_numbers'''