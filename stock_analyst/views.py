from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from . import models
from . import helpers
# Create your views here.


def index(request):
    return HttpResponse(render(request, 'index.html'))

def main(request):
    return HttpResponse(render(request, "main.html"))

def main_data_stream(request):
    # helpers.get_practice_data()
    helpers.get_data_from_api()
    # data = {}

    return JsonResponse(helpers.main_data_collector())