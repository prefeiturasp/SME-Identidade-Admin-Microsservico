"""URLs da API administrativa de permissões."""

from django.urls import path

from apps.keycloak_admin.permissoes.api.views import (
    ClientRoleDetailView,
    ClientRoleListCreateView,
    RealmRoleDetailView,
    RealmRoleListCreateView,
)

urlpatterns = [
    path(
        "permissoes/realm/",
        RealmRoleListCreateView.as_view(),
        name="permissoes-realm",
    ),
    path(
        "permissoes/realm/<str:nome>/",
        RealmRoleDetailView.as_view(),
        name="permissao-realm-detail",
    ),
    path(
        "permissoes/clientes/<str:client_uuid>/",
        ClientRoleListCreateView.as_view(),
        name="permissoes-cliente",
    ),
    path(
        "permissoes/clientes/<str:client_uuid>/<str:nome>/",
        ClientRoleDetailView.as_view(),
        name="permissao-cliente-detail",
    ),
]
