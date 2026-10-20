"""URLs da API administrativa de realms."""

from django.urls import path

from apps.keycloak_admin.realms.api.views import (
    RealmDetailView,
    RealmFinalidadesView,
    RealmListCreateView,
)

urlpatterns = [
    path(
        "realms/",
        RealmListCreateView.as_view(),
        name="realms",
    ),
    path(
        "realms/finalidades/",
        RealmFinalidadesView.as_view(),
        name="realm-finalidades",
    ),
    path(
        "realms/<str:nome>/",
        RealmDetailView.as_view(),
        name="realm-detail",
    ),
]
