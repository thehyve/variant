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
    
def search_by_interaction(search_terms, use_all_interactions = False):
    ''' Will return 
            a) every interaction where one of the fields is a match to 
        a search term, and every item referenced by such an interaction
            b) every study where one of the fields is a match to 
        a search term
        
        Right now works with one study, phenotype, genotype and panel.
        If 'use_all_interactions' is true we use all interactions for 
        the search, regardless of search terms. '''
    
    
    ''' We keep unpacking/overwriting 'output', this is because of memory 
        considerations. Should processing speed be considered more important, 
        different variables could be used. These could then perhaps be 
        added/'uniqued'/etc in one go.
        Because the 'output' variable keeps being overwritten, the ordering of 
        statements in the following sections can be significant. '''
    
    # Search through studies
    output = add_each_matching_item_to_results(Study.objects.all(), search_terms)
    results = list(set(output['results']))
    matches = list(set(output['matches']))
    study_id_to_interaction_id_mapping = {}
    
    # Search through interactions
    interactions = Interaction.objects.all()
    ''' 'interaction_mappings' is constructed to avoid having to deal with the
        Django 'ManyRelatedManager' at other moments. Also, having that dict 
        saves a couple for-loops later on in the template.'''
    interaction_mappings = create_interaction_mappings(interactions)
        
    output = {}
    if use_all_interactions:
        ''' If 'use_all_interactions' is true we use all interactions for 
            the search, regardless of search terms.
        '''
        return get_all_interactions_and_related_items(results, matches,
            search_terms, interactions, interaction_mappings)
    else:
        return get_relevant_interactions_and_related_items(results, matches,
            search_terms, interaction_mappings, interactions)
        
def get_relevant_interactions_and_related_items(results, matches,
        search_terms, interaction_mappings, interactions):
    output = add_each_matching_item_to_results(interactions, search_terms, 
        interaction_mappings)
    
    # Additional searches, not based on previously matched items
    ''' The following items must be searched through.
        This is done because these items may be search results, even though
        the interaction they are related to is not. '''
    studies_to_be_checked = list(set(output['studies_to_be_checked']))
    phenotypes_to_be_checked = list(set(output['phenotypes_to_be_checked']))
    genotypes_to_be_checked = list(set(output['genotypes_to_be_checked']))
    panels_to_be_checked = list(set(output['panels_to_be_checked']))
    ''' 'study_id_to_interaction_id_mapping' is filled when searching through 
        interactions. 
        Having that dict saves a for-loop later on in the template. '''
    study_id_to_interaction_id_mapping = output[
        'study_id_to_interaction_id_mapping']
    ''' Take the results from the interaction search, and add the
        interactions and their related studies, panels, phenotypes and genotypes 
        to the results.
        This is done because these items are all search results. ''' 
    results += list(set(output['results']))
    matches += list(set(output['matches']))
    
       
       
    # Additional searches, based on previously matched items
    ''' Search through all items referenced by all interactions that are not
        considered a search result. Those items may be relevant regardless
        of their interaction's relevance. Those items that match the search are 
        added to the overall search results.
    
        Add to our overall search results, those interactions that match the 
        newly added items, but not those that are already matches in and out of 
        themselves. '''
    to_be_checked = [[studies_to_be_checked, 'studies'],
         [phenotypes_to_be_checked, 'phenotypes'],
         [genotypes_to_be_checked, 'genotypes'],
         [panels_to_be_checked, 'panels']
        ]
    interactions_to_be_added = [] 
    for items, key in to_be_checked:
        output = add_each_matching_item_to_results(items, 
            search_terms)
        results += list(set(output['results']))
        matches += list(set(output['matches']))
        interactions_to_be_added += interactions_to_be_added_helper(
            output['results'], interactions, interaction_mappings, key, results)
    # Add all interactions that need to be displayed because of the items
    # they reference, to the search results
    output = add_each_item_to_results(interactions_to_be_added, search_terms)
    results += list(set(output['results']))
    matches += list(set(output['matches']))
    
    # Return final results
    return compile_final_results(results, matches, 
        study_id_to_interaction_id_mapping, interaction_mappings)        
    
def get_all_interactions_and_related_items(results, matches,
        search_terms, interactions, interaction_mappings):
    
    # Actual search doesn't really search, just adds all relevant items
    output = add_each_item_to_results(interactions, search_terms)
    
    ''' Take the results from the interaction search, and add the
        interactions and their related studies, panels, phenotypes and genotypes 
        to the results.
        This is done because these items are all search results. ''' 
    results += list(set(output['results']))
    matches += list(set(output['matches']))
    
    ''' 'study_id_to_interaction_id_mapping' is filled when searching through 
        interactions. 
        Having that dict saves a for-loop later on in the template. '''
    study_id_to_interaction_id_mapping = output[
        'study_id_to_interaction_id_mapping']
    
    # Search is now complete.   
    study_id_to_interaction_id_mapping = (
        clean_study_id_to_interaction_id_mapping(results, 
            study_id_to_interaction_id_mapping))
    
    # Return final results
    return compile_final_results(results, matches, 
        study_id_to_interaction_id_mapping, interaction_mappings)
    
def compile_final_results(results, matches, 
        study_id_to_interaction_id_mapping, interaction_mappings):
    results = list(set(results))
    matches = list(set(matches))
    formSets = utils.get_formsets_from_model_objects(results)
    study_id_to_interaction_id_mapping = (
        clean_study_id_to_interaction_id_mapping(results, 
            study_id_to_interaction_id_mapping))

    # Return final results
    return {'results': formSets, 'matches': matches, 
        'study_id_to_interaction_id_mapping': 
        study_id_to_interaction_id_mapping,
        'interaction_mappings': interaction_mappings}
    
def clean_study_id_to_interaction_id_mapping(results, 
            study_id_to_interaction_id_mapping):
    ''' Remove all mappings from study_id_to_interaction_id_mapping,
        that lead to interactions not present in the results.
        This way, the interactions header and column values only get printed if 
        one or more interactions will be printed afterward.
        
        This needs to be done in such a manner because, due to the strictness 
        of Django template language, it is not possible/easy to check whether 
        an item is present in a list or dict, when in a template. '''
    approved_interaction_ids = []    
    for item in results:
        if type(item) == Interaction:
            approved_interaction_ids.append(item.id)
    for study_id in study_id_to_interaction_id_mapping:
        for interaction_id in study_id_to_interaction_id_mapping[study_id]:
            if not interaction_id in approved_interaction_ids:
                study_id_to_interaction_id_mapping[study_id].remove(
                    interaction_id)   
    return study_id_to_interaction_id_mapping
    
def add_each_matching_item_to_results(items, search_terms, 
    interaction_mappings = {}):
    ''' Will add each item with a field value that matches a search term to the
        results, and will add the matched values to the matches 
    '''
    results = []
    matches = []
    studies_to_be_checked = []
    phenotypes_to_be_checked = []
    genotypes_to_be_checked = []
    panels_to_be_checked = []
    ''' 'study_id_to_interaction_id_mapping' is filled when searching through 
        interactions. 
        Having that dict saves a for-loop later on in the template. '''
    study_id_to_interaction_id_mapping = {} 
    
    for item in items:
        
        if type(item) == Interaction:
            ''' Make sure every item referenced by the interaction is checked
                to see if it should be included in the search result
            '''
            studies_to_be_checked.append(item.study)
            if not study_id_to_interaction_id_mapping.has_key(item.study.id):
                study_id_to_interaction_id_mapping[item.study.id] = []
            study_id_to_interaction_id_mapping[item.study.id].append(item.id)
            phenotypes_to_be_checked.append(
                interaction_mappings[item.id]['phenotypes'])
            genotypes_to_be_checked.append(
                interaction_mappings[item.id]['genotypes'])
            panels_to_be_checked.append(
                interaction_mappings[item.id]['panels'])   

        # Group field names and values together
        list_of_name_value_pairs = [
            (field.name, getattr(item,field.name)) 
            for field in item._meta.fields]

        for li in list_of_name_value_pairs:
            if not (li[0]=='id' or li[0]=='study'):
                val = str(li[1]).lower()
                for term in search_terms:
                    if term in val:
                        # A search term has been found in the field value
                        results.append(item)
                        matches.append(val)
                        if type(item) == Interaction:
                            ''' Add the study, genotype, phenotype and 
                                panel related to this interaction '''
                            if item.study != None:
                                results.append(item.study)
                            if len(item.phenotypes.all())!=0:
                                results.append(item.phenotypes.all()[0])
                            if len(item.genotypes.all())!=0:
                                results.append(item.genotypes.all()[0])
                            if len(item.panels.all())!=0:
                                results.append(item.panels.all()[0])
    return {'results': results, 
            'matches': matches, 
            'studies_to_be_checked': utils.clean_list(
                studies_to_be_checked), 
            'phenotypes_to_be_checked': utils.clean_list(
                phenotypes_to_be_checked), 
            'genotypes_to_be_checked': utils.clean_list(
                genotypes_to_be_checked), 
            'panels_to_be_checked': utils.clean_list(panels_to_be_checked), 
            'study_id_to_interaction_id_mapping': 
                study_id_to_interaction_id_mapping
    }
    
def add_each_item_to_results(items, search_terms):
    ''' Will add each item to the results, and will add the matched values
        (if any) to the matches. If the item in question is an interaction,
        the related study, genotype, phenotype and panel (if the interaction 
        has any such relation) are also added. This is to ensure that all the
        relevant information for the interaction is available.
    '''
    results = []
    matches = []
    ''' 'study_id_to_interaction_id_mapping' is filled when searching through 
        interactions. 
        Having that dict saves a for-loop later on in the template. '''
    study_id_to_interaction_id_mapping = {} 
    
    for item in items:
        results.append(item)
        list_of_name_value_pairs = [
            (field.name, getattr(item,field.name)) 
            for field in item._meta.fields]
          
        if type(item) == Interaction:
            ''' Add the study, genotype, phenotype and 
                panel related to this interaction '''
            results.append(item.study)
            if not study_id_to_interaction_id_mapping.has_key(item.study.id):
                study_id_to_interaction_id_mapping[item.study.id] = []
            study_id_to_interaction_id_mapping[item.study.id].append(item.id)
            if len(item.phenotypes.all())!=0:
                results.append(item.phenotypes.all()[0])
            if len(item.genotypes.all())!=0:
                results.append(item.genotypes.all()[0])
            if len(item.panels.all())!=0:
                results.append(item.panels.all()[0])
            
        for li in list_of_name_value_pairs:
            if not (li[0]=='id' or li[0]=='study'):
                val = str(li[1]).lower()
                for term in search_terms:
                    if term in val:
                        matches.append(val)
    return {'results': results, 'matches': matches, 
        'study_id_to_interaction_id_mapping': 
        study_id_to_interaction_id_mapping}
    
def interactions_to_be_added_helper(input, interactions, interaction_mappings, key, results):
    ''' Add the interactions that belong to newly-added items '''
    
    if len(input) != 0:
        if key == 'studies':
            '''# Add the interactions that belong to newly-added items
            output = [interaction for interaction in interactions if 
                interaction.study in input and 
                not interaction in results]
            return output '''
            
            ''' This no longer return the related interactions.
                Just because a study is relevant to the search, does not make
                each of that study's interactions relevant. '''
            return []
        else:
            # Add the interactions that belong to newly-added items
            output = [interaction for interaction in interactions if 
                interaction_mappings[interaction.id][key] in 
                input and not interaction in results]
            return output
    else:
        return []
        
def create_interaction_mappings(interactions):
    ''' 'interaction_mappings' is constructed to avoid having to deal with the
        Django 'ManyRelatedManager' at other moments. Also, having that dict 
        saves a couple for-loops later on in the template.'''
    interaction_mappings = {}
    
    ''' Make sure to clean each list that gets built based on the
        'interaction_mappings' var. We are about to fill it, 
        and we may put 'None' values in it.
        By cleaning the list afterward, with utils.clean_list/1,
        you avoid needing to do 'if not X == None'-like checks. '''
    for item in interactions:
        interaction_mappings[item.id] = {}
        if len(item.phenotypes.all())!=0:
            interaction_mappings[item.id]['phenotypes'
                ] = item.phenotypes.all()[0]
        else:
            interaction_mappings[item.id]['phenotypes'] = None
        if len(item.genotypes.all())!=0:
            interaction_mappings[item.id]['genotypes'] = item.genotypes.all()[0]
        else:
            interaction_mappings[item.id]['genotypes'] = None
        if len(item.panels.all())!=0:
            interaction_mappings[item.id]['panels'] = item.panels.all()[0]
        else:
            interaction_mappings[item.id]['panels'] = None        
    return interaction_mappings;