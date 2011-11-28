from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction
from itertools import chain
import utils 
from django.db.models import Q

def parse_terms(search_terms_string):
    search_terms = search_terms_string.lower().split(' ')
    search_terms = [term for term in search_terms if term!='']
    if len(search_terms) == 0:
        search_terms = ['']
    
    return search_terms    

def search(search_terms):
    a = Interaction.objects.all()
    b = Phenotype.objects.all()
    c = Panel.objects.all()
    d = Genotype.objects.all()
    e = Study.objects.all()
    items = chain(a,b,c,d,e)

    # Create model objects from search terms
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
    
    # Create formSets from model objects
    formSets = utils.get_formsets_from_model_objects(results)
    
    matches = list(set(matches))
    return {'results':formSets,'matches':matches}
    
def search_by_interaction(search_terms):
    ''' Will return every interaction where one of the fields is a match to 
        a search term, and every item referenced by such an interaction
    '''
    print 'entered search_by_interaction'
    # Right now works with one study, phenotype, genotype and panel.
    interactions = Interaction.objects.all()
    interaction_mappings = {}
    for item in interactions:
        interaction_mappings[item.id] = {}
        if len(item.phenotypes.all())!=0:
            #print '\n\na)',item.phenotypes.all()
            #print 'b)',item.phenotypes.all()[0].id,'\n\n'
            interaction_mappings[item.id]['phenotypes'] = item.phenotypes.all()[0]
        if len(item.genotypes.all())!=0:
            #print '\n\na)',item.genotypes.all()
            #print 'b)',item.genotypes.all()[0].id,'\n\n'
            interaction_mappings[item.id]['genotypes'] = item.genotypes.all()[0]
        if len(item.panels.all())!=0:
            #print '\n\na)',item.panels.all()
            #print 'b)',item.panels.all()[0].id,'\n\n'
            interaction_mappings[item.id]['panels'] = item.panels.all()[0]
       
    # Create model objects from search terms
    results = []
    matches = []
    studies_to_be_added = []
    phenotypes_to_be_added = []
    genotypes_to_be_added = []
    panels_to_be_added = []
    
    for item in interactions:
        t = type(item)
        #print '\n\n',t,':',item,'with id',item.id,
        
        list_of_name_value_pairs = [
            (field.name, getattr(item,field.name)) 
            for field in item._meta.fields]
        
        #print '\n\tlist_of_name_value_pairs:',list_of_name_value_pairs,
            
        for li in list_of_name_value_pairs:
            if not (li[0]=='id' or li[0]=='study'):
                val = str(li[1]).lower()
                for term in search_terms:
                    if term in val:
                        results.append(item)
                        matches.append(val)
                        ''' If one of the fields of an interaction is a match to 
                            a search term, make sure every item referenced by 
                            the interaction is added
                        '''
                        studies_to_be_added.append(item.study)
                        print 'added study',item.study
                        if interaction_mappings[item.id].has_key('phenotypes'):
                            phenotypes_to_be_added.append(
                                interaction_mappings[item.id]['phenotypes']
                            )
                        if interaction_mappings[item.id].has_key('genotypes'):
                            genotypes_to_be_added.append(
                                interaction_mappings[item.id]['genotypes']
                            )
                        if interaction_mappings[item.id].has_key('panels'):
                            panels_to_be_added.append(
                                interaction_mappings[item.id]['panels']
                            )

    studies_to_be_added = list(set(studies_to_be_added))
    phenotypes_to_be_added = list(set(phenotypes_to_be_added))
    genotypes_to_be_added = list(set(genotypes_to_be_added))
    panels_to_be_added = list(set(panels_to_be_added))
    output = search_by_interaction_helper(studies_to_be_added, search_terms)
    results += output['results']
    matches += output['matches']
    output = search_by_interaction_helper(phenotypes_to_be_added, search_terms)
    results += output['results']
    matches += output['matches']
    output = search_by_interaction_helper(genotypes_to_be_added, search_terms)
    results += output['results']
    matches += output['matches']
    output = search_by_interaction_helper(panels_to_be_added, search_terms)
    results += output['results']
    matches += output['matches']
    results = list(set(results))
    
    # Create formSets from model objects
    formSets = utils.get_formsets_from_model_objects(results)
    
    matches = list(set(matches))
    
    print 'leaving search_by_interaction'
    return {'results':formSets,'matches':matches}
    
def search_by_interaction_helper(items, search_terms):
    ''' Will add each item to the results, and will add the matched values
        (if any) to the matches
    '''
    results = []
    matches = []
    for item in items:
        results.append(item)
        list_of_name_value_pairs = [
            (field.name, getattr(item,field.name)) 
            for field in item._meta.fields]
        for li in list_of_name_value_pairs:
            if not (li[0]=='id' or li[0]=='study'):
                val = str(li[1]).lower()
                for term in search_terms:
                    if term in val:
                        matches.append(val)
    return {'results': results, 'matches': matches}