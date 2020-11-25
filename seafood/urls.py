from django.urls import path
from .views import *

urlpatterns = [
    path("", HomeView.as_view(), name='home'),
    path("view/", TableView.as_view(), name='view'),
    path("create/", CreateData.as_view(), name='create'),
    path("api/chart/", ChartData.as_view(), name='chart_api'),
]
