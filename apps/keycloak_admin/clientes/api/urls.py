"""URLs da API administrativa de clients."""

from django.urls import path

from apps.keycloak_admin.clientes.api.views import (
    ClientDetailView,
    ClientListCreateView,
    ClientSecretRotateView,
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
    path(
        "clientes/<uuid:client_uuid>/secret/rotacionar/",
        ClientSecretRotateView.as_view(),
        name="client-secret-rotate",
    ),
]
