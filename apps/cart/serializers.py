from rest_framework import serializers

from apps.menu.models import MenuItem

from .models import Cart, CartItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "name", "price", "img"]


class CartItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    menu_item = MenuItemSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "subtotal", "quantity", "menu_item", "price_snapshot"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField()

    class Meta:
        model = Cart
        fields = ["id", "items", "subtotal", "item_count"]


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()

    def validate_product_id(self, value):
        if not MenuItem.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid Product")
        return value

    # def validate_quantity(self, value):
    #     if value <= 0 :
    #         raise serializers.ValidationError("Quantity Must Be < then 0")
    #     return value


class UpdateItemCartSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    quantity = serializers.IntegerField()

    def validate_item_id(self, value):
        if not CartItem.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid item")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity Must Be < then 0")
        return value


class removeitemserializers(serializers.Serializer):
    item_id = serializers.UUIDField()

    def validate_item_id(self, value):
        if not CartItem.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid item")
        return value
