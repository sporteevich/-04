from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("kpi/", views.KPIApiView.as_view(), name="kpi"),
    path("revenue/", views.RevenueByDayApiView.as_view(), name="revenue"),
    path("top-models/", views.TopModelsApiView.as_view(), name="top_models"),
    path("manager-load/", views.ManagerLoadApiView.as_view(), name="manager_load"),
    path("stock/", views.StockApiView.as_view(), name="stock"),
]
