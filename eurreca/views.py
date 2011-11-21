from django.http import HttpResponse
from django.template import RequestContext, Context, loader
from eurreca.models import Study, Genotype, Phenotype, Panel, Interaction
from eurreca.forms import StudyFormSet, StudyForm, GenotypeFormSet, GenotypeForm, PhenotypeFormSet, PhenotypeForm, PanelForm, PanelFormSet, InteractionForm, InteractionFormSet
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory, inlineformset_factory
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.shortcuts import render
from django.http import Http404, HttpRequest
from django.core import serializers
import json
import pprint
from django.utils import simplejson
import utils 
import simple_search
import advanced_search
from itertools import chain

def index(request):
    user_list = User.objects.all()[:50]
    t = loader.get_template('index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

def do_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def do_login(request):
    message = ""
    messageType = ""
    
    # If the request does not contain the required keys, do nothing.
    if not request.POST.has_key('username') or not request.POST.has_key('password'):
        return render(request, 'index.html', {}) 
        
    # Retrieve relevant information from request before calling logout(), 
    # which wipes it
    username = request.POST['username']
    password = request.POST['password']
        
    # Make sure that you log any logged-in user out, before logging another in.
    logout(request)
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            messageType = 'positive'
            message = 'You have succesfully logged in.'
        else:
            messageType = 'negative'
            message = 'Your account appears to be disabled.'
    else:
        messageType = 'negative'
        message = 'The entered account information is invalid.'
    
    return render(request, 'index.html', 
        {'message' : message,
         'messageType' : messageType}) 
        
def study_list(request):
    qs = Study.objects.all()
    study_list = []
    if not len(qs) == 0:
        study_list = StudyFormSet(queryset=qs, prefix="study")
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
                
                # Fill forms to get new items, save the forms
                forms = utils.process_clientside_studydata(
                    json.loads(request.POST['returnObject']), study, None, request)
      
                # Study has been saved, return to study list
                message = "The study has been saved."
                messageType = "positive"
                print "The study has been saved."                
                return render(request, 'domain_views/study_list.html', 
                    {'message' : message,
                     'messageType' : messageType,
                     'study_list' : StudyFormSet(queryset=Study.objects.all(), 
                        prefix="study"),})
            except Exception as inst:
                print "in study create view"
                print type(inst)     # the exception instance
                print inst.args      # arguments stored in .args
                print inst    
                # Exception while reading or writing the study-related objects
                message =  "The study has not been saved."
                message += " Please review the errors and try again. "+str(inst)
                messageType = "negative"
                
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
        study = Study.objects.filter(pk=id)[0]
        try:
            # Make list of old items
            old_Genotypes = Genotype.objects.filter(study_id=id)
            old_Phenotypes = Phenotype.objects.filter(study_id=id)
            old_Panels = Panel.objects.filter(study_id=id)
            old_Interactions = Interaction.objects.filter(study_id=id)
            old_items = {'study':[study],'genotype':old_Genotypes,
                'phenotype':old_Phenotypes,'panel':old_Panels, 
                'interaction':old_Interactions}
  
            # Fill forms to get new items, save the forms
            forms = utils.process_clientside_studydata(
                json.loads(request.POST['returnObject']), study, formset, request)
            if formset[0].is_valid():
                study = formset[0].save()
            else: 
                raise ValueError('Some of the forms did not validate. {0}'.format(errors_to_string(formset[0].errors.items())))    
                
             # Remove old items, except study
            for gt in old_Genotypes: gt.delete()
            for pt in old_Phenotypes: pt.delete()
            for p in old_Panels: p.delete()
            for i in old_Interactions: i.delete()    
            
            # Study has been saved, return to study list
            message = "The study has been saved."
            messageType = "positive"
            print "The study has been saved."                
            return render(request, 'domain_views/study_list.html', 
                {'message' : message,
                 'messageType' : messageType,
                 'study_list' : StudyFormSet(queryset=Study.objects.all(), 
                    prefix="study"),})
        except Exception as inst:
            print "\nin study update view"
            print '\na)',type(inst)     # the exception instance
            print '\nb)',inst.args[0]
            if isinstance(inst.args[0], str):
                message =  "The study has not been saved."
                message += " Please review the errors and try again: "+str(inst.args[0])
                messageType = "negative"
                fs = utils.get_formsets_by_id(id)
                return render(request, 'domain_views/study_editing.html', 
                    {'formset' : fs['study'], 
                     'formsetGenotype' : fs['genotype'],
                     'formsetPhenotype' :  fs['phenotype'],
                     'formsetPanel' :  fs['panel'],
                     'formsetInteraction' :  fs['interaction'],
                     'message' : message,
                     'messageType' : messageType,})  
            print '\nc)',inst.args[0][0]      
            print '\nd)',inst.args[0][1]
            
            
            # Exception while reading or writing the study-related objects
            message =  "The study has not been saved."
            message += " Please review the errors and try again."+str(inst.args[0][0])
            messageType = "negative"

            return render(request, 'domain_views/study_editing.html', 
                {'formset' : inst.args[0][1]['formset'], 
                 'formsetGenotype' : inst.args[0][1]['formsetGenotype'],
                 'formsetPhenotype' :  inst.args[0][1]['formsetPhenotype'],
                 'formsetPanel' :  inst.args[0][1]['formsetPanel'],
                 'formsetInteraction' :  inst.args[0][1]['formsetInteraction'], 
                 'interactionValues' : inst.args[0][1]['interactionValues'], 
                 'message' : message,
                 'messageType' : messageType,})
    else:
        try:
            fs = utils.get_formsets_by_id(id)
            return render(request, 'domain_views/study_editing.html', 
                {'formset' : fs['study'], 
                 'formsetGenotype' : fs['genotype'],
                 'formsetPhenotype' :  fs['phenotype'],
                 'formsetPanel' :  fs['panel'],
                 'formsetInteraction' :  fs['interaction'],
                 'message' : message,
                 'messageType' : messageType,})
        except Study.DoesNotExist:
            return render(request, 'domain_views/study_list.html', 
                {'message' : "The requested study does not exist.",
                 'messageType' : "negative",
                 'study_list' : StudyFormSet(queryset=Study.objects.all(), 
                        prefix="study"),})  

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
    search_fields = ['']
    search_terms_string = ''
    advancedSearch = False
    if request.method == 'POST':
        if request.POST.has_key('search_type'):
            # This should probably check for the actual value instead
            advancedSearch = True
            
            # Determine which terms the user wants 
            # to search for in which fields
            search_terms_by_number = advanced_search.parse_terms(request.POST)
                    
            # Determine where the fields can be found        
            search_terms_by_number = advanced_search.locate_fields(
                search_terms_by_number)
            
            # Perform search    
            search_output = advanced_search.search(search_terms_by_number)
            
            # Create search terms string and term list (for user feedback)
            feedback =  advanced_search.get_feedback(
                search_terms_by_number)
            search_terms = feedback['search_terms']
            search_terms_string = feedback['search_terms_string']
            search_fields = feedback['search_fields']
        else:
            if not request.POST.has_key('search_terms'):
                message = "Please enter a search term."
                messageType = "negative"
                return render(request, 'search.html', 
                    {'message' : message,
                     'messageType' : messageType}) 
                     
            search_terms_string = request.POST['search_terms']
            
            # Parse search terms
            search_terms = simple_search.parse_terms(search_terms_string)
                
            # Perform search    
            search_output = simple_search.search(search_terms)
        
        return render(request, 'search.html', 
            {'message' : message,
             'messageType' : messageType,
             'matchedValues' : search_output['matches'],
             'searchTerms' : search_terms,
             'searchFields' : search_fields,
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