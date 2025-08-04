from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.


def index(request):
    return HttpResponse(render(request, 'index.html'))
def main(request):
    pass
