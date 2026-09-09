"""URLs da API administrativa de usuários."""

from django.urls import path

from apps.keycloak_admin.usuarios.api.views import (
    UsuarioClientRoleView,
    UsuarioDetailView,
    UsuarioEmailView,
    UsuarioGrupoView,
    UsuarioListCreateView,
    UsuarioRealmRoleView,
    UsuarioSenhaView,
)

urlpatterns = [
    path(
        "usuarios/",
        UsuarioListCreateView.as_view(),
        name="usuarios",
    ),
    path(
        "usuarios/<str:usuario_id>/",
        UsuarioDetailView.as_view(),
        name="usuario-detail",
    ),
    path(
        "usuarios/<str:usuario_id>/email/",
        UsuarioEmailView.as_view(),
        name="usuario-email",
    ),
    path(
        "usuarios/<str:usuario_id>/senha/",
        UsuarioSenhaView.as_view(),
        name="usuario-senha",
    ),
    path(
        "usuarios/<str:usuario_id>/grupos/",
        UsuarioGrupoView.as_view(),
        name="usuario-grupo",
    ),
    path(
        "usuarios/<str:usuario_id>/permissoes/realm/",
        UsuarioRealmRoleView.as_view(),
        name="usuario-realm-role",
    ),
    path(
        "usuarios/<str:usuario_id>/permissoes/cliente/",
        UsuarioClientRoleView.as_view(),
        name="usuario-client-role",
    ),
]
