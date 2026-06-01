from rest_framework import serializers

from .models import Address, Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "items",
            "status",
            "payment_method",
            "subtotal",
            "order_number",
            "delivery_address",
        ]


class CreateOrderSerializer(serializers.Serializer):
    delivery_address_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(["card", "cash"])

    def validate_delivery_address_id(self, value):
        if not Address.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid Address ")
        return value


class CancelOrderSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()

    def validate_order_id(self, value):
        if not Order.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid Order Id")
        return value


class UpdateOrderSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    status = serializers.ChoiceField(
        choices=[
            "PENDING",
            "CONFIRMED",
            "PERPARING",
            "DELIVERED",
            "CANCELLD",
        ]
    )

    def validate_order_id(self, value):
        if not Order.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid Order Id")
        return value


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "street",
            "full_name",
            "label",
            "country",
            "city",
            "state",
            "phone",
            "postcode",
            "is_default",
        ]
        read_only_fields = ["id"]
