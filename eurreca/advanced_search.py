from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction
from itertools import chain
import utils 
from django.db.models import Q
    
def search(search_terms):
    q_dicts = {'genotype':{},'phenotype':{},'panel':{},'study':{},
        'interaction':{}}
    q_objects = {'genotype':[],'phenotype':[],'panel':[],'study':[],
        'interaction':[]}

    # Create filters from search terms
    matches = []
    for number in search_terms:
        type  = search_terms[number]['type']
        field = search_terms[number]['field']
        term  = search_terms[number]['term']
        q_dicts[type][field+'__icontains'] = term
        matches.append(term)  
    
    # Create Q objects from filters
    for type in q_dicts:
        if not len(q_dicts[type]) == 0: 
            # Only do 'non-empty' searches.
            # An 'empty' search will yield ALL objects.
            q_objects[type] = [Q(**q_dicts[type])]
            
    
    # Create formSets from Q-objects
    formSets = utils.get_formsets_from_q_objects(q_objects)   
                    
    return {'results':formSets,'matches':matches}    
    
    
def parse_terms(post):
    ''' Retrieve the advanced search terms from dictionary, such as the 
        request.POST object. Return object is a dictionary organised first by
        number, then by 'field' and 'term' keys. '''
        
    search_terms_by_number = {}
    for key in post:
        if (key.startswith('search_field') or key.startswith('search_term')) and (not post[key] == ''):
            key_elements = key.split('_')
            number = key_elements[2]
            if not search_terms_by_number.has_key(number):
                search_terms_by_number[number] = {}
            search_terms_by_number[number][key_elements[1]] = post[key]
    return search_terms_by_number
    
def locate_fields(search_terms_by_number):
    ''' Returns search_terms_by_number with additional information concerning 
        the type of model object that the requested field is in, and the exact
        field name (rather than the user-readable representation that is 
        currently contained in the 'field' field). '''
        
    for number in search_terms_by_number:
        # Store user readable field name for later user feedback
        search_terms_by_number[number][
            'user_readable_field_name'] = search_terms_by_number[number]['field']
    
        # What type of model object?
        type = utils.get_model_type_from_term(
                    search_terms_by_number[number]['field']
                )
        search_terms_by_number[number]['type'] = type
        
        # In this model object, what field?
        field = utils.get_field_name_from_term(
                    search_terms_by_number[number]['field']
                )
        search_terms_by_number[number]['field'] = field
    
    return search_terms_by_number
    
def get_feedback(search_terms_by_number):
    ''' Returns a space-separated string of search terms, 
     and a list of search terms. '''
     
    search_terms_string = ''
    search_terms = []
    search_fields = []
    for number in search_terms_by_number:
        search_terms_string += search_terms_by_number[number]['term']+' '
        search_terms.append(search_terms_by_number[number]['term'])
        search_fields.append(search_terms_by_number[number][
            'user_readable_field_name'])
        
    return {'search_terms_string': search_terms_string, 
            'search_terms': search_terms, 
            'search_fields': search_fields}