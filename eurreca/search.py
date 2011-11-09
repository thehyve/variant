from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction
from itertools import chain

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
        list_of_name_value_pairs = [(field.name, getattr(item,field.name)) for field in item._meta.fields]
        for li in list_of_name_value_pairs:
            if not (li[0]=='id' or li[0]=='study_id'):
                val = str(li[1]).lower()
                for term in search_terms:
                    if term in val:
                        results.append(item)
                        matches.append(val)
    results = list(set(results))
    matches = list(set(matches))
    return {'results':results,'matches':matches}