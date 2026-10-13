"""Testes das views administrativas de realms."""

from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.keycloak_admin.exceptions import (
    OperacaoNaoPermitidaError,
    RecursoJaExisteError,
)

_SERVICE = "apps.keycloak_admin.realms.api.views.RealmService"

_REALM = {
    "id": "r1",
    "nome": "sme-apps",
    "nome_exibicao": "SME Apps",
    "habilitado": True,
    "oficial": True,
    "finalidade": None,
    "padrao": False,
    "protegido": True,
}


class TestRealmListCreateView:
    """Testes do endpoint de consulta e criação de realms."""

    def setup_method(self) -> None:
        """Inicializa o cliente HTTP de teste."""
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY=settings.API_KEY)

    @patch(_SERVICE)
    def test_get_consulta_realms(self, mock_service: MagicMock) -> None:
        """Deve listar os realms."""
        mock_service.return_value.consultar.return_value = [_REALM]

        response = self.client.get(reverse("realms"))

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [_REALM]
        mock_service.return_value.consultar.assert_called_once_with()

    @patch(_SERVICE)
    def test_post_cria_realm(self, mock_service: MagicMock) -> None:
        """Deve criar o realm com os dados validados."""
        response = self.client.post(
            reverse("realms"),
            {"nome": "sme-apps", "nome_exibicao": "SME Apps"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"mensagem": "Realm criado com sucesso."}
        mock_service.return_value.criar.assert_called_once_with(
            nome="sme-apps",
            nome_exibicao="SME Apps",
            habilitado=True,
            oficial=False,
        )

    @patch(_SERVICE)
    def test_post_rejeita_nome_invalido(
        self,
        mock_service: MagicMock,
    ) -> None:
        """Deve retornar 400 para nome fora do padrão."""
        response = self.client.post(
            reverse("realms"),
            {"nome": "sme apps"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "nome" in response.json()
        mock_service.return_value.criar.assert_not_called()

    @patch(_SERVICE)
    def test_post_realm_duplicado(self, mock_service: MagicMock) -> None:
        """Deve traduzir o conflito do Keycloak para erro de domínio."""
        mock_service.return_value.criar.side_effect = RecursoJaExisteError(
            "Recurso já existe no Keycloak."
        )

        response = self.client.post(
            reverse("realms"),
            {"nome": "sme-apps"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["codigo"] == "recurso_ja_existe"

    def test_exige_autenticacao(self) -> None:
        """Deve recusar requisições sem credenciais."""
        response = APIClient().get(reverse("realms"))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRealmDetailView:
    """Testes do endpoint de um realm específico."""

    def setup_method(self) -> None:
        """Inicializa o cliente HTTP de teste."""
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY=settings.API_KEY)

    @patch(_SERVICE)
    def test_get_consulta_realm(self, mock_service: MagicMock) -> None:
        """Deve retornar o realm consultado pelo nome."""
        mock_service.return_value.consultar.return_value = [_REALM]

        response = self.client.get(
            reverse("realm-detail", kwargs={"nome": "sme-apps"}),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _REALM
        mock_service.return_value.consultar.assert_called_once_with(
            nome="sme-apps",
        )

    @patch(_SERVICE)
    def test_patch_atualiza_realm(self, mock_service: MagicMock) -> None:
        """Deve atualizar o realm com os campos informados."""
        response = self.client.patch(
            reverse("realm-detail", kwargs={"nome": "sme-apps"}),
            {"habilitado": False},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "mensagem": "Realm atualizado com sucesso.",
        }
        mock_service.return_value.atualizar.assert_called_once_with(
            nome="sme-apps",
            habilitado=False,
        )

    @patch(_SERVICE)
    def test_patch_marca_oficial(self, mock_service: MagicMock) -> None:
        """Deve repassar a marcação de topologia oficial."""
        response = self.client.patch(
            reverse("realm-detail", kwargs={"nome": "sme-apps"}),
            {"oficial": True},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        mock_service.return_value.atualizar.assert_called_once_with(
            nome="sme-apps",
            oficial=True,
        )

    @patch(_SERVICE)
    def test_patch_sem_campos(self, mock_service: MagicMock) -> None:
        """Deve exigir ao menos um campo para atualização."""
        response = self.client.patch(
            reverse("realm-detail", kwargs={"nome": "sme-apps"}),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_service.return_value.atualizar.assert_not_called()

    @patch(_SERVICE)
    def test_patch_realm_protegido(self, mock_service: MagicMock) -> None:
        """Deve retornar erro de domínio ao desabilitar realm protegido."""
        mock_service.return_value.atualizar.side_effect = (
            OperacaoNaoPermitidaError(
                "O realm 'master' não pode ser desabilitado."
            )
        )

        response = self.client.patch(
            reverse("realm-detail", kwargs={"nome": "master"}),
            {"habilitado": False},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "codigo": "operacao_nao_permitida",
            "mensagem": "O realm 'master' não pode ser desabilitado.",
        }


class TestRealmFinalidadesView:
    """Testes do endpoint de finalidades de teste."""

    @override_settings(
        REALM_FINALIDADES_TESTE=["Sandbox", "UX"],
        REALM_FINALIDADE_PADRAO="Produção",
    )
    def test_get_lista_finalidades(self) -> None:
        """Deve listar as finalidades configuradas."""
        client = APIClient()
        client.credentials(HTTP_X_API_KEY=settings.API_KEY)

        response = client.get(reverse("realm-finalidades"))

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "finalidades": ["Sandbox", "UX"],
            "padrao": "Produção",
        }
