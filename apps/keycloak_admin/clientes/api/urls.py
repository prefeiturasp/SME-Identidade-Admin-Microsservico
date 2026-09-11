"""URLs da API administrativa de clients."""

from django.urls import path

from apps.keycloak_admin.clientes.api.views import (
    ClientDetailView,
    ClientListCreateView,
)

urlpatterns = [
    path(
        "clientes/",
        ClientListCreateView.as_view(),
        name="clients",
    ),
    path(
        "clientes/<str:client_uuid>/",
        ClientDetailView.as_view(),
        name="client-detail",
    ),
]
