# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    if request.GET.get('url'):
        url = request.GET['url'] #Getting URL
    else:
        feed = None
    return render(request, 'bpapp/index.html', {
        'feed' : feed,
    }
)