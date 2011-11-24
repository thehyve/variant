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
    qs = Study.objects.all()
    study_list = []
    if not len(qs) == 0:
        study_list = StudyFormSet(queryset=qs, prefix="study")
    t = loader.get_template('index.html')
    c = RequestContext( 
        request,
        {
            'study_list' : study_list,
            'logged_in' : request.user.is_authenticated(),
            'user' : request.user,
        }
    )
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
        try:
            study = formset[0].save()
            
            # Fill forms to get new items, save the forms
            forms = utils.process_clientside_studydata(
                json.loads(request.POST['returnObject']), study, None, request)
  
            # Study has been saved, show study
            message = "The study has been saved."
            messageType = "positive"                
            try:
                fs = utils.get_formsets_by_id(id)
                return render(request, 'domain_views/study_view.html', 
                    {'formset' : fs['study'], 
                     'formsetGenotype' : fs['genotype'],
                     'formsetPhenotype' :  fs['phenotype'],
                     'formsetPanel' :  fs['panel'],
                     'formsetInteraction' :  fs['interaction'],
                     'message' : message,
                     'messageType' : messageType,})         
            except Study.DoesNotExist:
                qs = Study.objects.all()
                study_list = []
                if not len(qs) == 0:
                    study_list = StudyFormSet(queryset=qs, prefix="study")
                return render(request, 'domain_views/study_list.html', 
                    {'message' : "The requested study does not exist.",
                     'messageType' : "negative",
                     'study_list' : study_list,})  
        except Exception as inst:
            print "\nin study create view"
            print '\na)',type(inst)     # the exception instance
            print '\nb)',inst.args[0]
            
            if isinstance(inst.args[0], str):
                # We received a string. So we did not receive a second 
                # argument (which should be a map of lists of forms)
                message =  "The study has not been saved."
                message += " Please review the errors and try again: "+str(inst.args[0])
                messageType = "negative"
                formset = StudyFormSet(queryset=Study.objects.none(), prefix="study")
                return render(request, 'domain_views/study_editing.html', 
                    {'formset' : formset, 
                     'message' : message,
                     'messageType' : messageType,
                     'year_list': utils.get_year_list(),})
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
                 'messageType' : messageType,
                 'year_list': utils.get_year_list(),}) 
    else:
        formset = StudyFormSet(queryset=Study.objects.none(), prefix="study")
    return render(request, 'domain_views/study_editing.html', 
        {'formset' : formset, 
         'message' : message,
         'messageType' : messageType,
         'year_list': utils.get_year_list(),})
         
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
        try:
            # Make list of old items
            # Copy items to enforce DB access now, 
            # rather than at one or more moments in the future
            old_Genotypes =    [g for g in  Genotype.objects.filter(study=id)]
            old_Phenotypes =   [p for p in Phenotype.objects.filter(study=id)]
            old_Panels =       [p for p in Panel.objects.filter(study=id)]
            old_Interactions = [i for i in Interaction.objects.filter(study=id)]
            # Remove old items, but do not empty their caches
            for gt in old_Genotypes: gt.delete()
            for pt in old_Phenotypes: pt.delete()
            for p in old_Panels: p.delete()
            for i in old_Interactions: i.delete()  
            # Right now, the study data has been removed!
            
            # Fill forms to get new items, save the forms
            forms = utils.process_clientside_studydata(
                json.loads(request.POST['returnObject']), Study.objects.get(pk=id), formset, request)
            if formset[0].is_valid():
                study = formset[0].save()
            else: 
                raise ValueError('Some of the forms did not validate. {0}'.format(utils.errors_to_string(formset[0].errors.items())))    
                
            # Study has been saved, show study
            message = "The study has been saved."
            messageType = "positive"                
            try:
                fs = utils.get_formsets_by_id(id)
                return render(request, 'domain_views/study_view.html', 
                    {'formset' : fs['study'], 
                     'formsetGenotype' : fs['genotype'],
                     'formsetPhenotype' :  fs['phenotype'],
                     'formsetPanel' :  fs['panel'],
                     'formsetInteraction' :  fs['interaction'],
                     'message' : message,
                     'messageType' : messageType,})         
            except Study.DoesNotExist:
                qs = Study.objects.all()
                study_list = []
                if not len(qs) == 0:
                    study_list = StudyFormSet(queryset=qs, prefix="study")
                return render(request, 'domain_views/study_list.html', 
                    {'message' : "The requested study does not exist.",
                     'messageType' : "negative",
                     'study_list' : study_list,})  
        except Exception as inst:
            print "\nin study update view"
            print '\na)',type(inst)     # the exception instance
            print '\nb)',inst.args[0]
            if isinstance(inst.args[0], str):
                # We received a string. So we did not receive a second 
                # argument (which should be a map of lists of forms)
                message =  "The study has not been saved."
                message += " Please review the errors and try again: "+str(inst.args[0])
                messageType = "negative"
                fs = utils.get_formsets_by_id(id)
                # Make sure these lists of items have already been processed at
                # least once, i.e. are not being loaded from DB right now!
                for gt in old_Genotypes: gt.save()
                for pt in old_Phenotypes: pt.save()
                for p in old_Panels: p.save()
                for i in old_Interactions: i.save() 
                return render(request, 'domain_views/study_editing.html', 
                    {'formset' : fs['study'], 
                     'formsetGenotype' : fs['genotype'],
                     'formsetPhenotype' :  fs['phenotype'],
                     'formsetPanel' :  fs['panel'],
                     'formsetInteraction' :  fs['interaction'],
                     'message' : message,
                     'messageType' : messageType,
                     'year_list': utils.get_year_list(),})  
            
            # Exception while reading or writing the study-related objects
            # Make sure these lists of items have already been processed at
            # least once, i.e. are not being loaded from DB right now!
            for gt in old_Genotypes: gt.save()
            for pt in old_Phenotypes: pt.save()
            for p in old_Panels: p.save()
            for i in old_Interactions: i.save() 
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
                 'messageType' : messageType,
                 'year_list': utils.get_year_list(),})
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
                 'messageType' : messageType,
                 'year_list': utils.get_year_list(),})
        except Study.DoesNotExist:
            qs = Study.objects.all()
            study_list = []
            if not len(qs) == 0:
                study_list = StudyFormSet(queryset=qs, prefix="study")
            return render(request, 'domain_views/study_list.html', 
                {'message' : "The requested study does not exist.",
                 'messageType' : "negative",
                 'study_list' : study_list,})  

def study_view(request, id):
    message = ""
    messageType = ""
    try:
        fs = utils.get_formsets_by_id(id)
        return render(request, 'domain_views/study_view.html', 
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
             'study_list' : Study.objects.all()[:50],})  
         
def study_remove(request, id):
    message = ""
    messageType = ""
    try:
        study = Study.objects.get(pk=id)
        a = Interaction.objects.filter(study=id)
        b = Phenotype.objects.filter(study=id)
        c = Panel.objects.filter(study=id)
        d = Genotype.objects.filter(study=study.id)
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

                 
    qs = Study.objects.all()
    study_list = []
    if not len(qs) == 0:
        study_list = StudyFormSet(queryset=qs, prefix="study")
    return render(request, 'domain_views/study_list.html', 
            {'message' : message,
             'messageType' : messageType,
             'study_list' : study_list,})  
             
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

def all(request):
    message = ""
    messageType = ""
        
    # Perform search    
    search_output = simple_search.search([''])

    return render(request, 'search.html', 
        {'message' : message,
         'messageType' : messageType,
         'formSets' : search_output['results']})             