from asgiref.sync import sync_to_async
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from . import models
from . import helpers
from mvp_stock_app.settings import USE_REAL_DATA
from .models import Dates


# Create your views here.


def index(request):
    return HttpResponse(render(request, 'main.html'))

def main(request):
    return HttpResponse(render(request, "index.html"))

async def main_data_stream(request):
    await helpers.update_model()
    data = await sync_to_async(helpers.main_data_collector)()
    return JsonResponse(data)

def db_health_check(request):
    """
    A simple view to check the database connection.
    .exists() is very efficient as it translates to a
    `SELECT 1 FROM ... LIMIT 1` query.
    """
    try:
        # Perform a lightweight, fast query
        is_db_alive = Dates.objects.exists()
        if is_db_alive or not is_db_alive: # This ensures the query runs
             return JsonResponse({"status": "ok", "database_connection": "alive"})
    except Exception as e:
        return JsonResponse({"status": "error", "database_connection": "dead", "error": str(e)}, status=500)