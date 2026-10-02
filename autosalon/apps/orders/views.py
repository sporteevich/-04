"""МОДУЛЬ 4 (ЗАКАЗЫ): API.

GET    /api/orders/              — список
POST   /api/orders/              — создать (авто уходит в «Забронирован»)
GET    /api/orders/{id}/         — детали
POST   /api/orders/{id}/complete/ — завершить (авто → «Продан»)
POST   /api/orders/{id}/cancel/   — отменить (авто → «В наличии»)
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD для заказов + каскадные действия."""
    queryset = Order.objects.select_related("client", "car", "car__brand", "manager").all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "order_type", "client", "manager"]
    search_fields = ["client__full_name", "car__model"]
    ordering_fields = ["created_at", "total_amount"]

    def perform_create(self, serializer):
        """Менеджер заказа — текущий пользователь."""
        serializer.save(manager=self.request.user)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Завершить заказ: авто становится проданным."""
        order = self.get_object()
        order.complete()
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Отменить заказ: авто возвращается в наличие."""
        order = self.get_object()
        order.cancel()
        return Response(self.get_serializer(order).data)
