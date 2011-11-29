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
    ''' Will return 
            a) every interaction where one of the fields is a match to 
        a search term, and every item referenced by such an interaction
            b) every study where one of the fields is a match to 
        a search term
        
        Right now works with one study, phenotype, genotype and panel.
    '''
    
    # Find all objects that need to be inspected
    studies = Study.objects.all()
    interactions = Interaction.objects.all()
    interaction_mappings = {}
    for item in interactions:
        interaction_mappings[item.id] = {}
        if len(item.phenotypes.all())!=0:
            interaction_mappings[item.id]['phenotypes'
                ] = item.phenotypes.all()[0]
        if len(item.genotypes.all())!=0:
            interaction_mappings[item.id]['genotypes'] = item.genotypes.all()[0]
        if len(item.panels.all())!=0:
            interaction_mappings[item.id]['panels'] = item.panels.all()[0]
       
    # Gather model objects based on search terms
    output = add_each_mathing_item_to_results(interactions, search_terms, 
        interaction_mappings)
    results = output['results']
    matches = output['matches']
    studies_to_be_added = output['studies_to_be_added']
    phenotypes_to_be_added = output['phenotypes_to_be_added']
    genotypes_to_be_added = output['genotypes_to_be_added']
    panels_to_be_added = output['panels_to_be_added']
    study_id_to_interaction_id_mapping = output[
        'study_id_to_interaction_id_mapping']
    
    output = add_each_mathing_item_to_results(studies, search_terms)
    results += output['results']
    matches += output['matches']
    
    # Add all items referneced by the interactions with matches
    output = add_each_item_to_results(list(set(studies_to_be_added)), 
        search_terms)
    results += output['results']
    matches += output['matches']
    
    output = add_each_item_to_results(list(set(phenotypes_to_be_added)), 
        search_terms)
    results += output['results']
    matches += output['matches']
    
    output = add_each_item_to_results(list(set(genotypes_to_be_added)), 
        search_terms)
    results += output['results']
    matches += output['matches']
    
    output = add_each_item_to_results(list(set(panels_to_be_added)), 
        search_terms)
    results += output['results']
    matches += output['matches']
    
    
    # Create formSets from model objects
    formSets = utils.get_formsets_from_model_objects(results)
    
    results = list(set(results))
    matches = list(set(matches))
    
    return {'results': formSets, 'matches': matches, 
        'study_id_to_interaction_id_mapping': 
        study_id_to_interaction_id_mapping}
    
def add_each_mathing_item_to_results(items, search_terms, 
    interaction_mappings = None):
    results = []
    matches = []
    studies_to_be_added = []
    phenotypes_to_be_added = []
    genotypes_to_be_added = []
    panels_to_be_added = []
    study_id_to_interaction_id_mapping = {}
    for item in items:
        list_of_name_value_pairs = [
            (field.name, getattr(item,field.name)) 
            for field in item._meta.fields]
        for li in list_of_name_value_pairs:
            if not (li[0]=='id' or li[0]=='study'):
                val = str(li[1]).lower()
                for term in search_terms:
                    if term in val:
                        results.append(item)
                        matches.append(val)
                        if not interaction_mappings == None:
                            ''' If one of the fields of an interaction is a 
                                match to a search term, make sure every item 
                                referenced by the interaction is added
                            '''
                            studies_to_be_added.append(item.study)
                            if not study_id_to_interaction_id_mapping.has_key(item.study.id):
                                study_id_to_interaction_id_mapping[item.study.id] = []
                            study_id_to_interaction_id_mapping[item.study.id].append(item.id)
                            if interaction_mappings[item.id].has_key(
                                'phenotypes'):
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
    return {'results': results, 'matches': matches, 'studies_to_be_added': 
        studies_to_be_added, 'phenotypes_to_be_added': phenotypes_to_be_added, 
        'genotypes_to_be_added': genotypes_to_be_added, 'panels_to_be_added': 
        panels_to_be_added, 'study_id_to_interaction_id_mapping': 
        study_id_to_interaction_id_mapping}
    
    
def add_each_item_to_results(items, search_terms):
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