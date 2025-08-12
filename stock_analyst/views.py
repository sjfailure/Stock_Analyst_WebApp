from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from . import models
from . import helpers
from mvp_stock_app.settings import USE_REAL_DATA
# Create your views here.


def index(request):
    return HttpResponse(render(request, 'index.html'))

def main(request):
    return HttpResponse(render(request, "main.html"))

def main_data_stream(request):
    if USE_REAL_DATA:
        helpers.get_data_from_api()
    else:
        helpers.get_practice_data()
    return JsonResponse(helpers.main_data_collector())