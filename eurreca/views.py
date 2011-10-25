from django.http import HttpResponse
from django.template import Context, loader
from eurreca.models import Study, Genotype, Phenotype
from eurreca.forms import StudyFormSet, StudyForm, GenotypeFormSet, GenotypeForm, PhenotypeFormSet, PhenotypeForm
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

def index(request):
    user_list = User.objects.all()[:50]
    book_list = Book.objects.all().order_by('name')[:50]
    author_list = Author.objects.all().order_by('name')[:50]
    t = loader.get_template('views.html')
    c = RequestContext( 
        request,
        {
            'user_list': user_list,
            'logged_in' : request.user.is_authenticated(),
            'user' : request.user,
            'book_list' : book_list,
            'author_list' : author_list,
            'templateNameJustForTesting' : t.name,
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
        all_went_well = True
        
        # Saving the study
        formset = StudyFormSet(request.POST, prefix="study")
        formsetGenotype = GenotypeFormSet(request.POST, prefix="genotype")
        study = None
        if formset[0].is_valid:
            try:
                study = formset[0].save()
            except:
                all_went_well = False
        else:
            all_went_well = False
            
        if all_went_well:
            # We can now save the genotypes with the correct study id
            try:
                formsetGenotypeData = []
                for form in formsetGenotype:
                    data = {}
                    for field in form:
                        data[field.name] = field.value()
                    data['study_id'] = study.id
                    formGenotype = GenotypeForm(data)
                    formGenotype.save()
                message =  "The study has been saved."
                messageType = "positive"
            except:
                all_went_well = False
        if all_went_well:
            return render(request, 'domain_views/study_list.html', 
                {'message' : message,
                 'messageType' : messageType,
                 'study_list' : Study.objects.all()[:50],})  
        else:
            print 'formset.errors',formset.errors
            message =  "The study has not been saved. "
            message += "Please review the errors and try again."
            messageType = "negative"
            # Everything that has been saved so far, needs to be deleted.
            if study != None:
                study.delete()
                gts = Genotype.objects.filter(study_id=study.id)
                for gt in gts:
                    if gt != None:
                        gt.delete()
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
        if formset[0].is_valid():
            study = formset[0].save()
            old_Genotypes = Genotype.objects.filter(study_id=id)
            '''
            #pp = pprint.PrettyPrinter(indent=4)
            #pp.pprint(request.POST)
            print "\n\tPost:"
            datas = {}
            for r in request.POST:
                datas[r] = request.POST[r]
                #print r,'->',request.POST[r]
            keylist = datas.keys()
            keylist.sort()    
            for key in keylist:
                print key,'->',datas[key]
            print "\tDone posting.\n"
            '''
            phenotype_data = {}
            genotype_data = {}
            interaction_data = {}
            unsorted_data = {}
            keylist = request.POST.keys()
            for key in keylist:
                if "MAX_NUM_FORMS" in key:
                    continue
                if "INITIAL_FORMS" in key:
                    continue
                if "TOTAL_FORMS" in key:
                    continue
                if key.startswith('phenotype'):
                    phenotype_data[key] = request.POST[key]
                    continue
                if key.startswith('genotype'):
                    genotype_data[key] = request.POST[key]
                    continue
                if key.startswith('interaction'):
                    interaction_data[key] = request.POST[key]
                    continue
                else:
                    unsorted_data[key] = request.POST[key]
            
            print "\n\tunsorted_data:"
            for key in unsorted_data:
                print key,"->",unsorted_data[key]
            print "\t...\n"
            
            print "\n\tinteraction_data:"
            for key in interaction_data:
                print key,"->",interaction_data[key]
            print "\t...\n"
            
            print "\n\tphenotype_data:"
            for key in phenotype_data:
                print key,"->",phenotype_data[key]
            print "\t...\n"
            
            print "\n\tgenotype_data:"
            for key in genotype_data:
                print key,"->",genotype_data[key]
            print "\t...\n"
            
            phenotype_data_numbered = {}
            for key in phenotype_data:
                str = key
                strList = str.split('-')
                if not phenotype_data_numbered.has_key(strList[1]):
                    phenotype_data_numbered[strList[1]] = {}
                phenotype_data_numbered[strList[1]][strList[2]] = phenotype_data[key]
            
            print "\n\tphenotype_data_numbered:"
            for key1 in phenotype_data_numbered:
                print key1
                form = PhenotypeForm(phenotype_data_numbered[key1])
                for key2 in phenotype_data_numbered[key1]:
                    print "\t",key2,"->",form.data[key2]
            print "{0} items.".format(len(phenotype_data_numbered))
            print "\t...\n"
            
            genotype_data_numbered = {}
            for key in genotype_data:
                str = key
                strList = str.split('-')
                if not genotype_data_numbered.has_key(strList[1]):
                    genotype_data_numbered[strList[1]] = {}
                genotype_data_numbered[strList[1]][strList[2]] = genotype_data[key]
            
            print "\n\tgenotype_data_numbered:"
            for key1 in genotype_data_numbered:
                print key1
                form = GenotypeForm(genotype_data_numbered[key1])
                for key2 in genotype_data_numbered[key1]:
                    print "\t",key2,"->",form.data[key2]
            print "{0} items.".format(len(genotype_data_numbered))
            print "\t...\n"
            
            
            '''
            phenotypeFormList = []
            phenotypeFormset = PhenotypeFormSet(Phenotype.objects.none(), prefix="phenotype")
            print "\n\tphenotypeFormList:"
            for form in phenotypeFormList:
                print form
            print "\t...\n"
            
            genotypeFormset = GenotypeFormSet(request.POST, prefix="genotype", max_num=len(genotype_data_numbered))
            print "\n\tgenotypeFormset:"
            for form in genotypeFormset:
                print form
            print "\t...\n"
            '''
            '''        
            data = serializers.serialize("json", Genotype.objects.filter(study_id=id))
            print json.dumps(json.loads(data), sort_keys = True, indent = 2)
            '''
            
            '''for gt in old_Genotypes:
                if gt != None:
                    gt.delete()'''
            
            message = "The study has been saved."
            messageType = "positive"
            return render(request, 'domain_views/study_list.html', 
                {'message' : message,
                 'messageType' : messageType,
                 'study_list' : Study.objects.all()[:50],})
        else:
            message =  "The study has not been saved."
            message += "Please review the errors and try again."
            messageType = "negative"
    else:
        try:
            formset = StudyFormSet(queryset=Study.objects.filter(pk=id), prefix="study")
            genotypeQueryset = Genotype.objects.filter(study_id=id)
            formsetGenotype = GenotypeFormSet(queryset=genotypeQueryset, prefix="genotype")
            if len(genotypeQueryset) == 0:
                '''print 'did not find any genotypes for study with id',id
                print "genotyes:",
                data = serializers.serialize("json", Genotype.objects.all())
                print json.dumps(json.loads(data), sort_keys = True, indent = 2)'''
                message += "This study does not yet have any genotypes related to it. "
                messageType = "negative"
            phenotypeQueryset = Phenotype.objects.filter(study_id=id)
            formsetPhenotype = PhenotypeFormSet(queryset=phenotypeQueryset, prefix="phenotype")
            if len(phenotypeQueryset) == 0:
                message += "This study does not yet have any phenotypes related to it. "
                messageType = "negative"
            
        except Study.DoesNotExist:
            return render(request, 'domain_views/study_list.html', 
                {'message' : "The requested study does not exist.",
                 'messageType' : "negative",
                 'study_list' : Study.objects.all()[:50],})

    return render(request, 'domain_views/study_editing.html', 
        {'formset' : formset, 
         'formsetGenotype' : formsetGenotype,
         'genotypeCount' : len(genotypeQueryset),
         'formsetPhenotype' : formsetPhenotype,
         'phenotypeCount' : len(phenotypeQueryset),
         'message' : message,
         'messageType' : messageType,})  

def study_view(request, id):
    message = ""
    messageType = ""
    try:
        formset = StudyFormSet(queryset=Study.objects.filter(pk=id))
        formsetGenotype = GenotypeFormSet(queryset=Genotype.objects.filter(study_id=id))
    except Study.DoesNotExist:
        return render(request, 'domain_views/study_list.html', 
            {'message' : "The requested study does not exist.",
             'messageType' : "negative",
             'study_list' : Study.objects.all()[:50],})

    return render(request, 'domain_views/study_view.html', 
        {'formset' : formset, 
         'formsetGenotype' : formsetGenotype,
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