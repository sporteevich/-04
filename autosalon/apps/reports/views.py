from rest_framework.views import APIView
from rest_framework.response import Response
from .services import ReportService


class KPIApiView(APIView):
    """GET /api/reports/kpi/?days=30"""
    def get(self, request):
        days = int(request.GET.get("days", 30))
        return Response(ReportService.kpi(days))


class RevenueByDayApiView(APIView):
    """GET /api/reports/revenue/"""
    def get(self, request):
        days = int(request.GET.get("days", 30))
        return Response(ReportService.revenue_by_day(days))


class TopModelsApiView(APIView):
    """GET /api/reports/top-models/"""
    def get(self, request):
        limit = int(request.GET.get("limit", 5))
        return Response(ReportService.top_models(limit))


class ManagerLoadApiView(APIView):
    """GET /api/reports/manager-load/"""
    def get(self, request):
        days = int(request.GET.get("days", 30))
        return Response(ReportService.manager_load(days))


class StockApiView(APIView):
    """GET /api/reports/stock/"""
    def get(self, request):
        return Response(ReportService.stock_status())
