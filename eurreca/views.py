from django.http import HttpResponse
from django.template import Context, loader
from eurreca.models import Book, Author
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

def index(request):
    user_list = User.objects.all()[:5]
    book_list = Book.objects.all().order_by('name')[:5]
    author_list = Author.objects.all().order_by('name')[:5]
    t = loader.get_template('views.html')
    c = Context({
        'user_list': user_list,
        'logged_in' : request.user.is_authenticated(),
        'user': request.user,
        'book_list': book_list,
        'author_list': author_list,
        'templateNameJustForTesting': t.name,
    })
    return HttpResponse(t.render(c))

@login_required
def editing_mode(request):
    return HttpResponseRedirect('/')
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
    
def specific_view(request):
    t = loader.get_template('specific_view.html')
    c = Context({
        'logged_in' : request.user.is_authenticated(),
        'user': request.user,
        'templateNameJustForTesting': t.name,
    })
    return HttpResponse(t.render(c))