from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .cart_service import (
    add_to_cart,
    get_or_create_active_cart,
    remove_cart_item,
    update_cart_item,
)
from .serializers import (
    AddToCartSerializer,
    CartItemSerializer,
    CartSerializer,
    UpdateItemCartSerializer,
    removeitemserializers,
)

# Create your views here.


def get_user_or_guest(request):
    if request.user.is_authenticated:
        return request.user, None

    if not request.session.session_key:
        request.session.create()

    return None, request.session.session_key


@api_view(["GET"])
@permission_classes([AllowAny])
def get_cart_api(request):
    user, guest_id = get_user_or_guest(request)

    cart = get_or_create_active_cart(user=user, guest_id=guest_id)

    return Response(CartSerializer(cart).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def AddToCartApi(request):
    serializer = AddToCartSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user, guest_id = get_user_or_guest(request)

    cart_item = add_to_cart(user=user, guest_id=guest_id, **serializer.validated_data)
    return Response(CartItemSerializer(cart_item).data)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def UpdateCartItemAPI(request):
    serializers = UpdateItemCartSerializer(data=request.data)

    if not serializers.is_valid():
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    user, guest_id = get_user_or_guest(request)

    item = update_cart_item(
        user=user,
        guest_id=guest_id,
        **serializers.validated_data,
    )

    return Response(CartItemSerializer(item).data)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def RemoveCartItemAPI(request):
    serializers = removeitemserializers(data=request.data)

    if not serializers.is_valid():
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    user, guest_id = get_user_or_guest(request)

    item = remove_cart_item(
        user=user,
        guest_id=guest_id,
        **serializers.validated_data,
    )
    return Response(CartItemSerializer(item).data)
