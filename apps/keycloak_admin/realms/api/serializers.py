"""Serializers da API administrativa de realms."""

from typing import Any

from django.conf import settings
from rest_framework import serializers

_PADRAO_NOME_REALM = r"^[A-Za-z0-9_-]+$"


class _FinalidadeMixin(serializers.Serializer):
    """Valida a finalidade contra a lista configurada no ambiente."""

    finalidade = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text=("Finalidade de teste do realm. Vazio remove a finalidade."),
    )

    def validate_finalidade(self, valor: str) -> str:
        """Valida se a finalidade pertence à lista configurada.

        Args:
            valor: Finalidade informada.

        Returns:
            Finalidade validada.

        Raises:
            serializers.ValidationError: Se a finalidade não for aceita.
        """
        opcoes = settings.REALM_FINALIDADES_TESTE

        if valor and valor not in opcoes:
            raise serializers.ValidationError(
                "Finalidade inválida. Opções: "
                f"{', '.join(opcoes) or 'nenhuma configurada'}."
            )

        return valor


class RealmCriarSerializer(_FinalidadeMixin):
    """Valida os dados para criação de um realm."""

    nome = serializers.RegexField(
        regex=_PADRAO_NOME_REALM,
        max_length=255,
        error_messages={
            "invalid": ("Use apenas letras, números, hífen ou sublinhado."),
        },
        help_text="Identificador do realm, usado nas URLs.",
    )
    nome_exibicao = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Nome apresentado nas telas do Keycloak.",
    )
    habilitado = serializers.BooleanField(
        required=False,
        default=True,
        help_text="Define se o realm será criado habilitado.",
    )
    oficial = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Define se o realm integra a topologia oficial SME.",
    )


class RealmAtualizarSerializer(_FinalidadeMixin):
    """Valida os dados para atualização de um realm."""

    nome_exibicao = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Novo nome de exibição do realm.",
    )
    habilitado = serializers.BooleanField(
        required=False,
        help_text="Define se o realm ficará habilitado.",
    )
    oficial = serializers.BooleanField(
        required=False,
        help_text="Define se o realm integra a topologia oficial SME.",
    )

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        """Valida os dados informados para atualização.

        Args:
            attrs: Dados recebidos para validação.

        Returns:
            Dados validados.

        Raises:
            serializers.ValidationError: Se nenhum campo for informado.
        """
        if not attrs:
            raise serializers.ValidationError(
                "Informe ao menos um campo para atualização."
            )

        return attrs


class RealmSerializer(serializers.Serializer):
    """Representa um realm na resposta da API."""

    id = serializers.CharField(allow_null=True)
    nome = serializers.CharField(allow_null=True)
    nome_exibicao = serializers.CharField(allow_null=True)
    habilitado = serializers.BooleanField()
    oficial = serializers.BooleanField(
        help_text="Indica se o realm integra a topologia oficial SME.",
    )
    finalidade = serializers.CharField(
        allow_null=True,
        help_text="Finalidade de teste do realm.",
    )
    protegido = serializers.BooleanField(
        help_text="Indica que o realm não pode ser desabilitado.",
    )
    padrao = serializers.BooleanField(
        help_text=(
            "Indica o realm usado quando nenhum realm de trabalho é "
            "informado."
        ),
    )


class FinalidadesSerializer(serializers.Serializer):
    """Representa as finalidades de teste aceitas."""

    finalidades = serializers.ListField(
        child=serializers.CharField(),
        help_text="Finalidades de teste aceitas.",
    )
    padrao = serializers.CharField(
        help_text="Rótulo do realm sem finalidade de teste.",
    )
