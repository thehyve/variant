from django.http import HttpResponse
from django.template import Context, loader
from eurreca.models import Book, Author, Study
from eurreca.forms import StudyFormSet, StudyForm
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render
from django.http import Http404

def index(request):
    user_list = User.objects.all()[:5]
    book_list = Book.objects.all().order_by('name')[:5]
    author_list = Author.objects.all().order_by('name')[:5]
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
    study_list = Study.objects.all()[:5]
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
        formset = StudyFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            # do something.
            print '\nsaved successfully\n'
            message = "The study has been saved."
            messageType = "positive"
        else:
            print '\ndid not save, form invalid',formset.errors,'\n'
            message =  "The study has not been saved."
            message += "Please review the errors and try again."
            messageType = "negative"
    else:
        formset = StudyFormSet(queryset=Study.objects.none())

    return render(request, 'domain_views/study_editing.html', 
        {'formset' : formset, 
         'message' : message,
         'messageType' : messageType,})
         
@login_required   
def study_update(request, id):
    message = ""
    messageType = ""
    if request.method == 'POST':
        formset = StudyFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            print '\nsaved successfully\n'
            message = "The study has been saved."
            messageType = "positive"
            return render(request, 'domain_views/study_list.html', 
            {'message' : message,
             'messageType' : messageType,
             'study_list' : Study.objects.all()[:5],})
        else:
            print '\ndid not save, form invalid',formset.errors,'\n'
            message =  "The study has not been saved."
            message += "Please review the errors and try again."
            messageType = "negative"
    else:
        try:
            formset = StudyFormSet(queryset=Study.objects.filter(pk=id))
        except Study.DoesNotExist:
            return render(request, 'domain_views/study_list.html', 
                {'message' : "The requested study does not exist.",
                 'messageType' : "negative",
                  'study_list' : Study.objects.all()[:5],})

    return render(request, 'domain_views/study_editing.html', 
        {'formset' : formset, 
         'message' : message,
         'messageType' : messageType,})  

def study_view(request, id):
    message = ""
    messageType = ""
    try:
        formset = StudyFormSet(queryset=Study.objects.filter(pk=id))
    except Study.DoesNotExist:
        return render(request, 'domain_views/study_list.html', 
            {'message' : "The requested study does not exist.",
             'messageType' : "negative",
             'study_list' : Study.objects.all()[:5],})

    return render(request, 'domain_views/study_view.html', 
        {'formset' : formset, 
         'message' : message,
         'messageType' : messageType,})           
         
def study_remove(request, id):
    message = ""
    messageType = ""
    try:
        # Does not yet handle related objects
        study = Study.objects.get(pk=id)
        study.delete()
        message = "Study was succesfully deleted."
        messageType = "positive"        
    except Study.DoesNotExist:
        message = "The requested study does not exist."
        messageType = "negative"

    return render(request, 'domain_views/study_list.html', 
            {'message' : message,
             'messageType' : messageType,
             'study_list' : Study.objects.all()[:5],})  