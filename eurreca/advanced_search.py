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
        if not search_terms[number].has_key('type') or not search_terms[number].has_key('field'):
            ''' This is a problem; we cannot search for this term 
                if we don't know where we should be looking. '''
            continue
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
            print 'q_dicts[type] ->', q_dicts[type]
            
            # The following does not work!
            # q_objects[type] = [Q(**q_dicts[type])]
            # See my question at 
            # http://stackoverflow.com/questions/8138919/trying-to-reduce-django-q-objects-with-operator-or-seems-to-result-in-reduction
            q_objects[type] = [Q(**{k: v}) for (k, v) in q_dicts[type].iteritems()]
        
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
        if not search_terms_by_number[number].has_key('field'):
            ''' It appears that the field that is to be searched, is not known.
                This is a problem; we cannot search for this term if we don't 
                know in which field we should be looking. '''
            continue
        if search_terms_by_number[number].has_key('term'):
            # Store user readable field name for later user feedback
            search_terms_by_number[number][
                'user_readable_field_name'] = search_terms_by_number[number]['field']
        
            # What type of model object?
            type = utils.get_model_from_search_term(
                        search_terms_by_number[number]['field']
                    )
            search_terms_by_number[number]['type'] = type
            
            # In this model object, what field?
            field = utils.get_field_from_search_term(
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
        if search_terms_by_number[number].has_key(
            'term'):
            search_terms_string += search_terms_by_number[number]['term']+' '
            search_terms.append(search_terms_by_number[number]['term'])
        else:
            search_terms.append('')
        if search_terms_by_number[number].has_key(
            'user_readable_field_name'):
            search_fields.append(search_terms_by_number[number][
                'user_readable_field_name'])
        else:
            search_fields.append('')
    return {'search_terms_string': search_terms_string, 
            'search_terms': search_terms, 
            'search_fields': search_fields}