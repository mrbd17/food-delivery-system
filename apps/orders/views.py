import requests
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import get_object_or_404, render
from django_countries import countries
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Address, Order
from .order_service import cancel_order, create_order, update_order_status
from .serializers import (
    AddressSerializer,
    CreateOrderSerializer,
    OrderSerializer,
    UpdateOrderSerializer,
)


class CountryListAPIView(APIView):
    def get(self, request):

        cached = cache.get("countries_list")

        if cached:
            return Response(cached)

        data = [{"code": code, "name": name} for code, name in countries]

        cache.set("countries_list", data, 60 * 60 * 24)

        return Response(data)


class DetectCountryAPIView(APIView):
    def get(self, request):
        ip = request.META.get("REMOTE_ADDR")

        cache_key = f"geo_{ip}"
        cached = cache.get(cache_key)

        if cached:
            return Response(cached)

        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()

            results = {
                "country_code": data.get("country"),
            }

            cache.set(cache_key, results, 60 * 60 * 24)
            return Response(results)

        except:
            return Response({"country_code": "EG"})


# Create your views here.


def checkoutpage(request):
    return render(request, "checkout.html")


@login_required
def track_order_page(request, pk):
    order = get_object_or_404(Order, id=pk, user=request.user)
    return render(request, "ordertracking.html")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def CreateOrderView(request):
    serializer = CreateOrderSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    order = create_order(user=request.user, **serializer.validated_data)

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class ListOrderView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class DetailOrderView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


@api_view(["GET"])
@permission_classes([IsAdminUser])
def AllOrders():
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request):
        serializer = UpdateOrderSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.validated_data["order_id"]
        new_status = serializer.validated_data["status"]

        try:
            order = update_order_status(
                user=request.user,
                order_id=order_id,
                new_status=new_status,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Order Status Updated Successfully",
                "order_id": order.id,
                "new_status": order.status,
            }
        )


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        try:
            order = cancel_order(user=request.user, order_id=order_id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Order was Canncelled",
                "order_id": order.id,
            }
        )


class AddressViewSet(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
