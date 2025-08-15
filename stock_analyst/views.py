from asgiref.sync import sync_to_async
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from . import models
from . import helpers
from mvp_stock_app.settings import USE_REAL_DATA
# Create your views here.


def index(request):
    return HttpResponse(render(request, 'main.html'))

def main(request):
    return HttpResponse(render(request, "index.html"))

async def main_data_stream(request):
    await helpers.update_model()
    data = await sync_to_async(helpers.main_data_collector)()
    return JsonResponse(data)