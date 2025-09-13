import logging

from asgiref.sync import sync_to_async
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from . import models
from . import helpers
from mvp_stock_app.settings import USE_REAL_DATA
from .models import Dates, Datapoints


# Create your views here.


# def index(request):
#     return HttpResponse(render(request, 'main.html'))

def main(request):
    return HttpResponse(render(request, "main.html"))

def main_data_stream(request):
    helpers.update_model()
    data = helpers.main_data_collector()
    return JsonResponse(data)

def detail(request, company_id):
    data = helpers.detail_build(company_id)
    logging.warning(f'detail(): context data for html={data}')
    return HttpResponse(render(request, template_name="detail.html", context=data))

def detail_data_stream(request, company_id, category_id, period):
    logging.warning(f'detail_data_stream(): API endpoint activated: call for company_id={company_id}, '
                    f'category_id={category_id}, period={period}')
    output = helpers.detail_view_data_collector(company_id, category_id, period)
    return JsonResponse(output)
