"""Serviço de administração de realms no Keycloak."""

import logging
from typing import Any

from django.conf import settings

from apps.keycloak_admin.admin_kc import KeycloakAdminService
from apps.keycloak_admin.exceptions import OperacaoNaoPermitidaError

logger = logging.getLogger(__name__)

ATRIBUTO_TOPOLOGIA_OFICIAL = "topologia_oficial"
ATRIBUTO_FINALIDADE_TESTE = "finalidade_teste"


class RealmService:
    """Centraliza as operações administrativas de realms no Keycloak.

    Diferente dos demais serviços, que operam dentro do realm
    configurado, este atua sobre os próprios realms do servidor. A
    exclusão não é oferecida: desabilitar o realm é a forma reversível
    de retirá-lo de uso.

    A marcação de topologia oficial SME e a finalidade de teste ficam
    em atributos do próprio realm, para que a classificação acompanhe
    o realm entre consultas e não dependa de configuração da aplicação.
    """

    def __init__(
        self,
        admin: KeycloakAdminService | None = None,
    ) -> None:
        """Inicializa o serviço de administração de realms.

        Args:
            admin: Serviço responsável pela comunicação com o Keycloak.
                Quando não informado, uma nova instância é criada usando
                as configurações padrão da aplicação.
        """
        self.admin = admin or KeycloakAdminService()

    def criar(
        self,
        nome: str,
        nome_exibicao: str | None = None,
        habilitado: bool = True,
        oficial: bool = False,
        finalidade: str | None = None,
    ) -> None:
        """Cria um realm no servidor Keycloak.

        O nome do realm compõe as URLs de autenticação e não pode ser
        alterado depois, por isso só o nome de exibição e a situação
        ficam editáveis.

        Args:
            nome: Identificador do realm.
            nome_exibicao: Nome apresentado nas telas do Keycloak.
            habilitado: Define se o realm será criado habilitado.
            oficial: Define se o realm integra a topologia oficial SME.
            finalidade: Finalidade de teste do realm.

        Raises:
            OperacaoNaoPermitidaError: Ao criar um realm oficial
                desabilitado.
        """
        if oficial and not habilitado:
            raise OperacaoNaoPermitidaError(
                "Realm da topologia oficial não pode ser desabilitado."
            )

        payload: dict[str, Any] = {
            "realm": nome,
            "enabled": habilitado,
            "attributes": {
                ATRIBUTO_TOPOLOGIA_OFICIAL: self._formatar_booleano(oficial),
                ATRIBUTO_FINALIDADE_TESTE: finalidade or "",
            },
        }

        if nome_exibicao:
            payload["displayName"] = nome_exibicao

        logger.info(
            "Criando realm no Keycloak.",
            extra={"realm": nome},
        )

        self.admin.executar(
            self.admin.cliente.create_realm,
            payload=payload,
            skip_exists=False,
        )

    def consultar(
        self,
        nome: str | None = None,
    ) -> list[dict[str, Any]]:
        """Consulta realms do servidor Keycloak.

        Quando ``nome`` é informado, apenas esse realm é consultado;
        caso contrário, todos os realms visíveis ao usuário
        administrativo são retornados.

        Args:
            nome: Identificador do realm a consultar.

        Returns:
            Lista de realms com os campos normalizados para o contrato
            interno da aplicação.
        """
        logger.debug(
            "Consultando realms no Keycloak.",
            extra={"realm": nome},
        )

        if nome is not None:
            realm = self.admin.executar(
                self.admin.cliente.get_realm,
                realm_name=nome,
            )

            return [self._normalizar_realm(realm)]

        realms = self.admin.executar(
            self.admin.cliente.get_realms,
        )

        return [self._normalizar_realm(realm) for realm in realms]

    def atualizar(
        self,
        nome: str,
        nome_exibicao: str | None = None,
        habilitado: bool | None = None,
        oficial: bool | None = None,
        finalidade: str | None = None,
    ) -> None:
        """Atualiza parcialmente um realm.

        Realms da topologia oficial, o ``master`` e o realm em que esta
        aplicação opera não podem ser desabilitados. A situação atual do
        realm é consultada antes, de modo que retirar a marcação oficial
        e desabilitar exige duas operações explícitas.

        Os atributos do Keycloak guardam também configurações internas
        do realm; por isso a marcação oficial e a finalidade são gravadas
        sobre o mapa atual, preservando as demais chaves.

        Args:
            nome: Identificador do realm.
            nome_exibicao: Novo nome de exibição.
            habilitado: Define se o realm ficará habilitado.
            oficial: Define se o realm integra a topologia oficial SME.
            finalidade: Finalidade de teste do realm; vazio a remove.

        Raises:
            OperacaoNaoPermitidaError: Ao tentar desabilitar um realm
                protegido.
        """
        payload: dict[str, Any] = {}

        if nome_exibicao is not None:
            payload["displayName"] = nome_exibicao

        if habilitado is not None:
            payload["enabled"] = habilitado

        altera_atributos = oficial is not None or finalidade is not None

        if habilitado is False or altera_atributos:
            atual = self.admin.executar(
                self.admin.cliente.get_realm,
                realm_name=nome,
            )

            if habilitado is False:
                self._validar_desabilitacao(nome, atual, oficial)

            if altera_atributos:
                payload["attributes"] = self._mesclar_atributos(
                    atual,
                    oficial,
                    finalidade,
                )

        if not payload:
            return

        logger.info(
            "Atualizando realm no Keycloak.",
            extra={"realm": nome},
        )

        self.admin.executar(
            self.admin.cliente.update_realm,
            realm_name=nome,
            payload=payload,
        )

    def _validar_desabilitacao(
        self,
        nome: str,
        atual: dict[str, Any],
        oficial: bool | None,
    ) -> None:
        """Impede desabilitar realm protegido ou marcado como oficial.

        A marcação pedida na mesma operação também conta, para que não
        seja possível tornar o realm oficial já desabilitado.

        Args:
            nome: Identificador do realm.
            atual: Representação atual do realm no Keycloak.
            oficial: Marcação de topologia oficial pedida na operação.

        Raises:
            OperacaoNaoPermitidaError: Se o realm não puder ser
                desabilitado.
        """
        if oficial or self._normalizar_realm(atual)["protegido"]:
            raise OperacaoNaoPermitidaError(
                f"O realm '{nome}' não pode ser desabilitado."
            )

    def _mesclar_atributos(
        self,
        atual: dict[str, Any],
        oficial: bool | None,
        finalidade: str | None,
    ) -> dict[str, Any]:
        """Aplica a classificação sobre os atributos atuais do realm.

        O mapa de atributos é enviado inteiro ao Keycloak, por isso as
        chaves que não fazem parte da classificação são mantidas.

        Args:
            atual: Representação atual do realm no Keycloak.
            oficial: Nova marcação de topologia oficial, se informada.
            finalidade: Nova finalidade de teste, se informada.

        Returns:
            Atributos atualizados do realm.
        """
        atributos = dict(atual.get("attributes") or {})

        if oficial is not None:
            atributos[ATRIBUTO_TOPOLOGIA_OFICIAL] = self._formatar_booleano(
                oficial
            )

        if finalidade is not None:
            atributos[ATRIBUTO_FINALIDADE_TESTE] = finalidade

        return atributos

    @staticmethod
    def listar_finalidades() -> list[str]:
        """Lista as finalidades de teste aceitas para os realms.

        A lista é definida por ambiente, permitindo ajustar as opções
        sem alterar o código.

        Returns:
            Finalidades configuradas, na ordem informada.
        """
        return list(settings.REALM_FINALIDADES_TESTE)

    @staticmethod
    def finalidade_padrao() -> str:
        """Retorna o rótulo do realm sem finalidade de teste.

        Realm sem finalidade está em uso normal; o rótulo exibido para
        esse caso é definido por ambiente.

        Returns:
            Rótulo configurado, por padrão ``"Produção"``.
        """
        return str(settings.REALM_FINALIDADE_PADRAO)

    @staticmethod
    def _realms_protegidos() -> set[str]:
        """Retorna os realms protegidos independentemente de atributo.

        O ``master`` concentra o usuário administrativo e o realm
        configurado é onde a aplicação autentica seus clientes; ambos
        continuam protegidos mesmo sem a marcação oficial.

        Returns:
            Conjunto com os identificadores protegidos.
        """
        return {"master", settings.KEYCLOAK_REALM}

    @staticmethod
    def _formatar_booleano(valor: bool) -> str:
        """Formata um booleano como atributo do Keycloak.

        Atributos de realm só aceitam texto.

        Args:
            valor: Valor booleano.

        Returns:
            ``"true"`` ou ``"false"``.
        """
        return "true" if valor else "false"

    @classmethod
    def _normalizar_realm(
        cls,
        realm: dict[str, Any],
    ) -> dict[str, Any]:
        """Normaliza os dados de um realm para o contrato da aplicação.

        A representação do Keycloak traz dezenas de configurações
        internas; apenas as relevantes para a gestão são expostas.
        ``protegido`` indica se o realm pode ser desabilitado,
        ``padrao`` marca o realm usado quando nenhum é escolhido na
        requisição e ``finalidade`` vazia é devolvida como ``None``.

        Args:
            realm: Dados do realm retornados pelo Keycloak.

        Returns:
            Dicionário contendo os dados do realm no formato utilizado
            internamente pela aplicação.
        """
        atributos = realm.get("attributes") or {}
        oficial = atributos.get(ATRIBUTO_TOPOLOGIA_OFICIAL) == "true"

        return {
            "id": realm.get("id"),
            "nome": realm.get("realm"),
            "nome_exibicao": realm.get("displayName"),
            "habilitado": realm.get("enabled", False),
            "oficial": oficial,
            "finalidade": atributos.get(ATRIBUTO_FINALIDADE_TESTE) or None,
            "padrao": realm.get("realm") == settings.KEYCLOAK_REALM,
            "protegido": oficial
            or realm.get("realm") in cls._realms_protegidos(),
        }
