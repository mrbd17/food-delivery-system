from django.urls import path

from . import views

urlpatterns = [
    path("checkout/", views.checkoutpage, name="checkout_page"),
    path("<uuid:pk>/tracking/", views.track_order_page, name="track-order"),
    path("list/", views.ListOrderView.as_view(), name="list_orders"),
    path(
        "update-status/<uuid:pk>/",
        views.UpdateOrderStatusView.as_view(),
        name="update-status",
    ),
    path(
        "cancel-order/<uuid:order_id>/",
        views.CancelOrderView.as_view(),
        name="cnacel-order",
    ),
    path("create/", views.CreateOrderView, name="ceate_order"),
    path("<uuid:pk>/", views.DetailOrderView.as_view(), name="order_detail"),
    path(
        "<uuid:order_id>/status/",
        views.UpdateOrderStatusView.as_view(),
        name="update_status",
    ),
    path(
        "<uuid:order_id>/cancel/", views.CancelOrderView.as_view(), name="cancel_order"
    ),
    path("owner/", views.AllOrders, name="all_orders"),
    path("addresses/", views.AddressViewSet.as_view(), name="addresses"),
    path(
        "address/<uuid:pk>/", views.AddressDetailView.as_view(), name="address_detail"
    ),
    path("countries/", views.CountryListAPIView.as_view()),
    path("detect_country/", views.DetectCountryAPIView.as_view()),
]
