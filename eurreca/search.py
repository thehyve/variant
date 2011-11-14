from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction
from itertools import chain
import utils 
from django.db.models import Q

def simple_search(search_terms):
    a = Interaction.objects.all()
    b = Phenotype.objects.all()
    c = Panel.objects.all()
    d = Genotype.objects.all()
    e = Study.objects.all()
    items = chain(a,b,c,d,e)

    results = []
    matches = []
    for item in items:
        list_of_name_value_pairs = [
            (field.name, getattr(item,field.name)) 
            for field in item._meta.fields]
        for li in list_of_name_value_pairs:
            if not (li[0]=='id' or li[0]=='study_id'):
                val = str(li[1]).lower()
                for term in search_terms:
                    if term in val:
                        results.append(item)
                        matches.append(val)
    results = list(set(results))
    formSets = utils.get_formsets_from_model_objects(results)
    matches = list(set(matches))
    return {'results':formSets,'matches':matches}
    
    
def advanced_search(search_terms):
    q_dicts = {'genotype':{},'phenotype':{},'panel':{},'study':{},
        'interaction':{}}
    q_objects = {'genotype':[],'phenotype':[],'panel':[],'study':[],
        'interaction':[]}

    matches = []
            
    for number in search_terms:
        type  = search_terms[number]['type']
        field = search_terms[number]['field']
        term  = search_terms[number]['term']
        q_dicts[type][field+'__icontains'] = term
        matches.append(term)  
    
    for type in q_dicts:
        if not len(q_dicts[type]) == 0: 
            # Only do 'non-empty' searches.
            # An 'empty' search will yield ALL objects.
            q_objects[type] = [Q(**q_dicts[type])]
            #print 'q_objects[',type,']',q_dicts[type]
    #print 'Num gts:',len(q_objects['genotype'])
    #print 'Num pts:',len(q_objects['phenotype'])
    #print 'Num ps: ',len(q_objects['panel'])
    #print 'Num ss: ',len(q_objects['study'])
    #print 'Num ias:',len(q_objects['interaction']) 
    formSetsBefore = utils.get_formsets_from_q_objects(q_objects)   
    formSets = {'genotype':None,'phenotype':None,'panel':None,'study':None,
        'interaction':None}     
    for key in formSets:
        if not formSetsBefore[key] == None:
            #print key,'  ',len(formSetsBefore[key])
            #for hobbit in formSetsBefore[key]:
            #    print "\t",hobbit
            if len(formSetsBefore[key])>0:
                formSets[key] = formSetsBefore[key]
    return {'results':formSets,'matches':matches}    