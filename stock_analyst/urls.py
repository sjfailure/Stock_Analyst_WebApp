from django.urls import path
from . import views

urlpatterns = [
    # path('test', views.index, name='index'),
    path('', views.main, name='main'),
    path('data_stream', views.main_data_stream, name='data_stream'),
    # path('health-check', views.db_health_check, name='health_check'),
    path('detail/<int:company_id>', views.detail, name='detail_view'),
    path('detail/data_stream/<int:company_id>/<int:period>/<int:category_id>', views.detail_data_stream)
]

