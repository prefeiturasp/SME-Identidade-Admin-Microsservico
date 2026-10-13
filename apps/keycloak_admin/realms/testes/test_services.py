"""Testes dos serviços administrativos de realms."""

from typing import Any
from unittest.mock import Mock

from django.test import SimpleTestCase, override_settings

from apps.keycloak_admin.exceptions import OperacaoNaoPermitidaError
from apps.keycloak_admin.realms.services import RealmService


@override_settings(KEYCLOAK_REALM="COTIC")
class RealmServiceTest(SimpleTestCase):
    """Testes do serviço de administração de realms."""

    def setUp(self) -> None:
        """Prepara o mock do serviço administrativo do Keycloak."""
        self.admin = Mock()
        self.service = RealmService(admin=self.admin)

    def _mockar_realm_atual(self, realm: dict[str, Any]) -> None:
        """Faz a consulta do realm atual devolver ``realm``."""

        def executar(operacao: Any, **kwargs: Any) -> Any:
            if operacao is self.admin.cliente.get_realm:
                return realm
            return None

        self.admin.executar.side_effect = executar

    def _payload_atualizacao(self) -> dict[str, Any]:
        """Retorna o payload enviado ao ``update_realm``."""
        chamada = next(
            c
            for c in self.admin.executar.call_args_list
            if c.args[0] is self.admin.cliente.update_realm
        )
        payload: dict[str, Any] = chamada.kwargs["payload"]
        return payload

    def test_criar_realm(self) -> None:
        """Deve criar o realm com nome de exibição, situação e marcação."""
        self.service.criar(
            nome="sme-apps",
            nome_exibicao="SME Apps",
            habilitado=True,
            oficial=True,
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.create_realm,
            payload={
                "realm": "sme-apps",
                "enabled": True,
                "attributes": {
                    "topologia_oficial": "true",
                    "finalidade_teste": "",
                },
                "displayName": "SME Apps",
            },
            skip_exists=False,
        )

    def test_criar_realm_sem_nome_exibicao(self) -> None:
        """Não deve enviar displayName quando ausente ou vazio."""
        self.service.criar(nome="sme-apps", nome_exibicao="")

        payload = self.admin.executar.call_args.kwargs["payload"]

        self.assertEqual(
            payload,
            {
                "realm": "sme-apps",
                "enabled": True,
                "attributes": {
                    "topologia_oficial": "false",
                    "finalidade_teste": "",
                },
            },
        )

    def test_criar_realm_com_finalidade(self) -> None:
        """Deve gravar a finalidade de teste no atributo do realm."""
        self.service.criar(nome="sandbox", finalidade="Sandbox")

        payload = self.admin.executar.call_args.kwargs["payload"]

        self.assertEqual(
            payload["attributes"]["finalidade_teste"],
            "Sandbox",
        )

    def test_impede_criar_realm_oficial_desabilitado(self) -> None:
        """Deve recusar criar realm oficial já desabilitado."""
        with self.assertRaises(OperacaoNaoPermitidaError):
            self.service.criar(nome="x", habilitado=False, oficial=True)

        self.admin.executar.assert_not_called()

    def test_consultar_todos_os_realms(self) -> None:
        """Deve listar os realms normalizados com marcação e proteção."""
        self.admin.executar.return_value = [
            {
                "id": "r1",
                "realm": "sme-apps",
                "displayName": "SME Apps",
                "enabled": True,
                "attributes": {"topologia_oficial": "true"},
            },
            {
                "id": "r2",
                "realm": "teste",
                "attributes": {"finalidade_teste": "UX"},
            },
            {"id": "r3", "realm": "COTIC", "enabled": True},
        ]

        resultado = self.service.consultar()

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_realms,
        )
        self.assertEqual(
            resultado,
            [
                {
                    "id": "r1",
                    "nome": "sme-apps",
                    "nome_exibicao": "SME Apps",
                    "habilitado": True,
                    "oficial": True,
                    "finalidade": None,
                    "padrao": False,
                    "protegido": True,
                },
                {
                    "id": "r2",
                    "nome": "teste",
                    "nome_exibicao": None,
                    "habilitado": False,
                    "oficial": False,
                    "finalidade": "UX",
                    "padrao": False,
                    "protegido": False,
                },
                {
                    "id": "r3",
                    "nome": "COTIC",
                    "nome_exibicao": None,
                    "habilitado": True,
                    "oficial": False,
                    "finalidade": None,
                    "padrao": True,
                    "protegido": True,
                },
            ],
        )

    def test_consultar_realm_por_nome(self) -> None:
        """Deve consultar um único realm pelo nome."""
        self.admin.executar.return_value = {
            "id": "r1",
            "realm": "sme-apps",
            "enabled": True,
        }

        resultado = self.service.consultar(nome="sme-apps")

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_realm,
            realm_name="sme-apps",
        )
        self.assertEqual(resultado[0]["nome"], "sme-apps")

    def test_atualizar_nome_exibicao_sem_consultar(self) -> None:
        """Não deve consultar o realm quando só o nome de exibição muda."""
        self.service.atualizar(nome="teste", nome_exibicao="Teste")

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.update_realm,
            realm_name="teste",
            payload={"displayName": "Teste"},
        )

    def test_desabilitar_realm_nao_oficial(self) -> None:
        """Deve desabilitar realm que não é protegido."""
        self._mockar_realm_atual({"realm": "teste", "attributes": {}})

        self.service.atualizar(nome="teste", habilitado=False)

        self.assertEqual(self._payload_atualizacao(), {"enabled": False})

    def test_impede_desabilitar_realm_oficial(self) -> None:
        """Deve recusar desabilitar realm marcado como oficial."""
        self._mockar_realm_atual(
            {
                "realm": "sme-apps",
                "attributes": {"topologia_oficial": "true"},
            },
        )

        with self.assertRaises(OperacaoNaoPermitidaError):
            self.service.atualizar(nome="sme-apps", habilitado=False)

    def test_impede_desabilitar_e_marcar_oficial_juntos(self) -> None:
        """Deve recusar desabilitar ao marcar como oficial na mesma ação."""
        self._mockar_realm_atual({"realm": "teste", "attributes": {}})

        with self.assertRaises(OperacaoNaoPermitidaError):
            self.service.atualizar(
                nome="teste",
                habilitado=False,
                oficial=True,
            )

    def test_impede_desabilitar_realms_fixos(self) -> None:
        """Deve recusar desabilitar o master e o realm configurado."""
        for nome in ("master", "COTIC"):
            self._mockar_realm_atual({"realm": nome, "attributes": {}})

            with self.assertRaises(OperacaoNaoPermitidaError):
                self.service.atualizar(nome=nome, habilitado=False)

    def test_marcar_oficial_preserva_atributos(self) -> None:
        """Deve gravar a marcação sem perder os demais atributos."""
        self._mockar_realm_atual(
            {"realm": "teste", "attributes": {"cibaInterval": "5"}},
        )

        self.service.atualizar(nome="teste", oficial=True)

        self.assertEqual(
            self._payload_atualizacao(),
            {
                "attributes": {
                    "cibaInterval": "5",
                    "topologia_oficial": "true",
                },
            },
        )

    def test_desmarcar_oficial_com_realm_sem_atributos(self) -> None:
        """Deve tratar realm sem atributos ao remover a marcação."""
        self._mockar_realm_atual({"realm": "teste"})

        self.service.atualizar(nome="teste", oficial=False)

        self.assertEqual(
            self._payload_atualizacao(),
            {"attributes": {"topologia_oficial": "false"}},
        )

    def test_definir_e_limpar_finalidade(self) -> None:
        """Deve gravar a finalidade e aceitar vazio para removê-la."""
        self._mockar_realm_atual(
            {
                "realm": "teste",
                "attributes": {"cibaInterval": "5"},
            },
        )

        self.service.atualizar(nome="teste", finalidade="UX")
        self.assertEqual(
            self._payload_atualizacao(),
            {
                "attributes": {
                    "cibaInterval": "5",
                    "finalidade_teste": "UX",
                },
            },
        )

        self.admin.executar.reset_mock()
        self.service.atualizar(nome="teste", finalidade="")
        self.assertEqual(
            self._payload_atualizacao()["attributes"]["finalidade_teste"],
            "",
        )

    @override_settings(REALM_FINALIDADES_TESTE=["Sandbox", "UX"])
    def test_listar_finalidades(self) -> None:
        """Deve devolver as finalidades configuradas no ambiente."""
        self.assertEqual(
            RealmService.listar_finalidades(),
            ["Sandbox", "UX"],
        )

    @override_settings(REALM_FINALIDADE_PADRAO="Uso regular")
    def test_finalidade_padrao(self) -> None:
        """Deve devolver o rótulo configurado para uso normal."""
        self.assertEqual(RealmService.finalidade_padrao(), "Uso regular")

    def test_atualizar_sem_campos_nao_chama_keycloak(self) -> None:
        """Não deve chamar o Keycloak sem campos para atualizar."""
        self.service.atualizar(nome="teste")

        self.admin.executar.assert_not_called()
