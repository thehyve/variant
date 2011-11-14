from django.http import HttpResponse
from django.template import Context, loader
from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction
from eurreca.forms import StudyFormSet, StudyForm, GenotypeFormSet, GenotypeForm, PhenotypeFormSet, PhenotypeForm, PanelForm, PanelFormSet, InteractionForm, InteractionFormSet
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory, inlineformset_factory
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render
from django.http import Http404
from django.core import serializers
import json
import pprint
from django.utils import simplejson
import utils 
import search

def index(request):
    user_list = User.objects.all()[:50]
    t = loader.get_template('views.html')
    c = RequestContext( 
        request,
        {
            'user_list': user_list,
            'logged_in' : request.user.is_authenticated(),
            'user' : request.user,
        }
    )
    return HttpResponse(t.render(c))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def study_list(request):
    study_list = Study.objects.all()[:50]
    t = loader.get_template('domain_views/study_list.html')
    c = RequestContext( 
        request,
        {
            'study_list' : study_list,
            'logged_in' : request.user.is_authenticated(),
            'user' : request.user,
        }
    )
    return HttpResponse(t.render(c))

@login_required   
def study_create(request):
    message = ""
    messageType = ""
    if request.method == 'POST':
        formset = StudyFormSet(request.POST, prefix="study")
        forms = {}

        if formset[0].is_valid():
            study = formset[0].save()
            try:
                # There are no old items. Create and pass the object anyway,
                # so that we can re-use 'update'-functions
                old_items = {'study':[],'genotype':[],'phenotype':[],
                    'panel':[], 'interaction':[]}  
                
                # Fill forms to get new items, save the forms
                forms = utils.process_clientside_studydata(
                    json.loads(request.POST['returnObject']), study, old_items)
      
                # Study has been saved, return to study list
                message = "The study has been saved."
                messageType = "positive"
                print "The study has been saved."                
                return render(request, 'domain_views/study_list.html', 
                    {'message' : message,
                     'messageType' : messageType,
                     'study_list' : Study.objects.all()[:50],})
            except Exception as inst:
                print "in study create view"
                print type(inst)     # the exception instance
                print inst.args      # arguments stored in .args
                print inst    
                # Exception while reading or writing the study-related objects
                message =  "The study has not been saved."
                message += " Please review the errors and try again. "+str(inst)
                messageType = "negative"
                
                # Remove the new study
                study.delete()
                
                return render(request, 'domain_views/study_editing.html', 
                    {'formset' : formset, 
                     'message' : message,
                     'messageType' : messageType,})  
        else:
            # Study form did not validate
            message =  "The study has not been saved."
            message += "Please review the errors and try again."
            messageType = "negative"
            return render(request, 'domain_views/study_editing.html', 
                {'formset' : formset, 
                 'message' : message,
                 'messageType' : messageType,})  
    else:
        formset = StudyFormSet(queryset=Study.objects.none(), prefix="study")
    return render(request, 'domain_views/study_editing.html', 
        {'formset' : formset, 
         'message' : message,
         'messageType' : messageType,})
         
@login_required   
def study_update(request, id):
    message = ""
    messageType = ""
    if request.method == 'POST':
        formset = StudyFormSet(request.POST, prefix="study")
        old_Genotypes = []
        old_Phenotypes = []
        old_Panels = []
        old_Interactions = []
        forms = {}

        if formset[0].is_valid():
            old_study = Study.objects.get(pk=id)
            study = formset[0].save()
            try:
                # Make list of old items, so that the could be restored if
                # necessary.
                old_Genotypes = Genotype.objects.filter(study_id=id)
                old_Phenotypes = Phenotype.objects.filter(study_id=id)
                old_Panels = Panel.objects.filter(study_id=id)
                old_Interactions = Interaction.objects.filter(study_id=id)
                old_items = {'study':[old_study],'genotype':old_Genotypes,
                    'phenotype':old_Phenotypes,'panel':old_Panels, 
                    'interaction':old_Interactions}
                
                # Remove old items, except study
                for gt in old_Genotypes: gt.delete()
                for pt in old_Phenotypes: pt.delete()
                for p in old_Panels: p.delete()
                for i in old_Interactions: i.delete()      
                
                # Fill forms to get new items, save the forms
                forms = utils.process_clientside_studydata(
                    json.loads(request.POST['returnObject']), study, old_items)
      
                # Study has been saved, return to study list
                message = "The study has been saved."
                messageType = "positive"
                print "The study has been saved."                
                return render(request, 'domain_views/study_list.html', 
                    {'message' : message,
                     'messageType' : messageType,
                     'study_list' : Study.objects.all()[:50],})
            except Exception as inst:
                print "in study update view"
                print type(inst)     # the exception instance
                print inst.args      # arguments stored in .args
                print inst    
                # Exception while reading or writing the study-related objects
                message =  "The study has not been saved."
                message += " Please review the errors and try again."+str(inst)
                messageType = "negative"
                
                # Remove the new study and re-save the old study
                study.delete()
                old_study.save()
                
                return render(request, 'domain_views/study_editing.html', 
                    {'formset' : formset, 
                     'message' : message,
                     'messageType' : messageType,})  
        else:
            # Study form did not validate
            message =  "The study has not been saved."
            message += "Please review the errors and try again."
            messageType = "negative"
            return render(request, 'domain_views/study_editing.html', 
                {'formset' : formset, 
                 'message' : message,
                 'messageType' : messageType,})  
            
    else:
        try:
            fs = utils.get_formsets_by_id(id)
        except Study.DoesNotExist:
            return render(request, 'domain_views/study_list.html', 
                {'message' : "The requested study does not exist.",
                 'messageType' : "negative",
                 'study_list' : Study.objects.all()[:50],})
        finally:
            return render(request, 'domain_views/study_editing.html', 
                {'formset' : fs['study'], 
                 'formsetGenotype' : fs['genotype'],
                 'formsetPhenotype' :  fs['phenotype'],
                 'formsetPanel' :  fs['panel'],
                 'formsetInteraction' :  fs['interaction'],
                 'message' : message,
                 'messageType' : messageType,})  

def study_view(request, id):
    message = ""
    messageType = ""
    try:
        fs = utils.get_formsets_by_id(id)
    except Study.DoesNotExist:
        return render(request, 'domain_views/study_list.html', 
            {'message' : "The requested study does not exist.",
             'messageType' : "negative",
             'study_list' : Study.objects.all()[:50],})
    finally:
        return render(request, 'domain_views/study_view.html', 
            {'formset' : fs['study'], 
                 'formsetGenotype' : fs['genotype'],
                 'formsetPhenotype' :  fs['phenotype'],
                 'formsetPanel' :  fs['panel'],
                 'formsetInteraction' :  fs['interaction'],
             'message' : message,
             'messageType' : messageType,})           
         
def study_remove(request, id):
    message = ""
    messageType = ""
    try:
        study = Study.objects.get(pk=id)
        a = Interaction.objects.filter(study_id=id)
        b = Phenotype.objects.filter(study_id=id)
        c = Panel.objects.filter(study_id=id)
        d = Genotype.objects.filter(study_id=study.id)
        items = chain(a,b,c,d)
        study.delete()
        for item in items:
            if item != None:
                item.delete()
        message = "The study has been deleted."
        messageType = "positive"        
    except Study.DoesNotExist:
        message = "The requested study does not exist."
        messageType = "negative"

    return render(request, 'domain_views/study_list.html', 
            {'message' : message,
             'messageType' : messageType,
             'study_list' : Study.objects.all()[:50],})  
             
def search_view(request):
    message = ""
    messageType = ""
    search_terms = ['']
    search_terms_string = ''
    advancedSearch = False
    if request.method == 'POST':
        if request.POST.has_key('search_type'):
            # This should probably check for the actual value instead
            print 'advanced search'
            advancedSearch = True
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
            from_string_to_proper_field_name = {
                "Study id":"study_id",
                "Pubmed id":"pubmed_id",
                "Year of publication":"year_of_publication",
                "Micronutrient":"micronutrient",
                "Gene":"geno",
                "SNP ref":"snp_ref",
                "Phenotype name":"phenotype_name",
                "SNP variant":"snp_variant"
            }
            
            # Determine which terms are meant to be searched in which fields
            search_terms_by_number = {}
            for key in request.POST:
                if (key.startswith('search_field') or key.startswith('search_term')) and (not request.POST[key] == ''):
                    key_elements = key.split('_')
                    number = key_elements[2]
                    if not search_terms_by_number.has_key(number):
                        search_terms_by_number[number] = {}
                    search_terms_by_number[number][key_elements[1]] = request.POST[key]
                    
            # Determine where the fields can be found        
            for number in search_terms_by_number:
                type = from_term_to_model_type[
                            search_terms_by_number[number]['field']
                        ]
                search_terms_by_number[number]['type'] = type
                field = from_string_to_proper_field_name[
                            search_terms_by_number[number]['field']
                        ]
                search_terms_by_number[number]['field'] = field
                search_terms_string += search_terms_by_number[number]['term']+' '

            search_output = search.advanced_search(search_terms_by_number)
            
        else:
            print 'simple search'
            search_terms_string = request.POST['search_terms']
            search_terms = search_terms_string.lower().split(' ')
            search_terms = [term for term in search_terms if term!='']
            if len(search_terms) == 0:
                search_terms = ['']
                
            search_output = search.simple_search(search_terms)
        
        return render(request, 'search.html', 
            {'message' : message,
             'messageType' : messageType,
             'matchedValues' : search_output['matches'],
             'searchTerms' : search_terms,
             'previousSearchString' : search_terms_string,
             'formSets' : search_output['results'],
             'advancedSearch' : advancedSearch})  
    
    return render(request, 'search.html', 
            {'message' : message,
             'messageType' : messageType})  
             
def advanced_search_view(request):
    message = ""
    messageType = ""
    return render(request, 'search.html', 
            {'message' : message,
             'messageType' : messageType,
             'advancedSearch' : True})               