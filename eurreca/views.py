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
import eurecca_utils 

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
                old_items = {'study':[],'genotype':[],'phenotype':[],'panel':[], 'interaction':[]}  
                
                # Fill forms to get new items, save the forms
                forms = eurecca_utils.process_clientside_studydata(
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
        formsetGenotype = GenotypeFormSet(queryset=Genotype.objects.none(), prefix="genotype")
        
    return render(request, 'domain_views/study_editing.html', 
        {'formset' : formset, 
         'formsetGenotype' : formsetGenotype,
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
                old_items = {'study':[old_study],'genotype':old_Genotypes,'phenotype':old_Phenotypes,'panel':old_Panels, 'interaction':old_Interactions}
                
                # Remove old items, except study
                for gt in old_Genotypes: gt.delete()
                for pt in old_Phenotypes: pt.delete()
                for p in old_Panels: p.delete()
                for i in old_Interactions: i.delete()      
                
                # Fill forms to get new items, save the forms
                forms = eurecca_utils.process_clientside_studydata(
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
            formset = StudyFormSet(queryset=Study.objects.filter(pk=id), prefix="study")
            formsetGenotype = GenotypeFormSet(queryset=Genotype.objects.filter(study_id=id), prefix="genotype")
            formsetPhenotype = PhenotypeFormSet(queryset=Phenotype.objects.filter(study_id=id), prefix="phenotype")
            formsetPanel = PanelFormSet(queryset=Panel.objects.filter(study_id=id), prefix="panel")
            formsetInteraction = InteractionFormSet(queryset=Interaction.objects.filter(study_id=id), prefix="interaction")
        except Study.DoesNotExist:
            return render(request, 'domain_views/study_list.html', 
                {'message' : "The requested study does not exist.",
                 'messageType' : "negative",
                 'study_list' : Study.objects.all()[:50],})
        finally:
            return render(request, 'domain_views/study_editing.html', 
                {'formset' : formset, 
                 'formsetGenotype' : formsetGenotype,
                 'formsetPhenotype' : formsetPhenotype,
                 'formsetPanel' : formsetPanel,
                 'formsetInteraction' : formsetInteraction,
                 'message' : message,
                 'messageType' : messageType,})  

def study_view(request, id):
    message = ""
    messageType = ""
    
    try:
        formset = StudyFormSet(queryset=Study.objects.filter(pk=id), prefix="study")
        formsetGenotype = GenotypeFormSet(queryset=Genotype.objects.filter(study_id=id), prefix="genotype")
        formsetPhenotype = PhenotypeFormSet(queryset=Phenotype.objects.filter(study_id=id), prefix="phenotype")
        formsetPanel = PanelFormSet(queryset=Panel.objects.filter(study_id=id), prefix="panel")
        formsetInteraction = InteractionFormSet(queryset=Interaction.objects.filter(study_id=id), prefix="interaction")
    except Study.DoesNotExist:
        return render(request, 'domain_views/study_list.html', 
            {'message' : "The requested study does not exist.",
             'messageType' : "negative",
             'study_list' : Study.objects.all()[:50],})
    finally:
        return render(request, 'domain_views/study_view.html', 
            {'formset' : formset, 
             'formsetGenotype' : formsetGenotype,
             'formsetPhenotype' : formsetPhenotype,
             'formsetPanel' : formsetPanel,
             'formsetInteraction' : formsetInteraction,
             'message' : message,
             'messageType' : messageType,})           
         
def study_remove(request, id):
    message = ""
    messageType = ""
    try:
        study = Study.objects.get(pk=id)
        gts = Genotype.objects.filter(study_id=study.id)
        study.delete()
        for gt in gts:
            if gt != None:
                gt.delete()
        message = "The study has been deleted."
        messageType = "positive"        
    except Study.DoesNotExist:
        message = "The requested study does not exist."
        messageType = "negative"

    return render(request, 'domain_views/study_list.html', 
            {'message' : message,
             'messageType' : messageType,
             'study_list' : Study.objects.all()[:50],})  