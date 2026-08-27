"""Rotas da API administrativa de sessões."""

from django.urls import path

from apps.keycloak_admin.sessoes.api.views import (
    SessaoListView,
    SessaoLogoutView,
)

urlpatterns = [
    path(
        "sessoes/<str:usuario_id>/",
        SessaoListView.as_view(),
        name="sessao-list",
    ),
    path(
        "sessoes/<str:usuario_id>/encerrar/",
        SessaoLogoutView.as_view(),
        name="sessao-logout",
    ),
]
