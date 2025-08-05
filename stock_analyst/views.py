from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


from model.DatabaseAdmin import data_wrangling_for_main
import model.model_main
# Create your views here.


def index(request):
    return HttpResponse(render(request, 'index.html'))

def main(request):
    return HttpResponse(render(request, "main.html"))

def main_data_stream(request):
    data = data_wrangling_for_main()
    return JsonResponse(data)