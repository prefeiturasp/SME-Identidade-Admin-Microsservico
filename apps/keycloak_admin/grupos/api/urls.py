"""Rotas da API administrativa de grupos."""

from django.urls import path

from apps.keycloak_admin.grupos.api.views import (
    GrupoClientRoleView,
    GrupoDetailView,
    GrupoListCreateView,
    GrupoRealmRoleView,
)

urlpatterns = [
    path(
        "grupos/",
        GrupoListCreateView.as_view(),
        name="grupo-list-create",
    ),
    path(
        "grupos/<str:grupo_id>/",
        GrupoDetailView.as_view(),
        name="grupo-detail",
    ),
    path(
        "grupos/<str:grupo_id>/roles/realm/",
        GrupoRealmRoleView.as_view(),
        name="grupo-realm-role",
    ),
    path(
        "grupos/<str:grupo_id>/roles/cliente/<str:client_uuid>/",
        GrupoClientRoleView.as_view(),
        name="grupo-client-role",
    ),
]
