"""Serializers da API administrativa de permissões."""

from typing import Any

from rest_framework import serializers


class RoleCriarSerializer(serializers.Serializer):
    """Valida os dados para criação de uma permissão."""

    nome = serializers.CharField(
        max_length=255,
        help_text="Nome da permissão.",
    )
    descricao = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Descrição da permissão.",
    )
    atributos = serializers.DictField(
        required=False,
        help_text="Atributos personalizados da permissão.",
    )


class RoleConsultaSerializer(serializers.Serializer):
    """Valida os parâmetros para consulta de permissões."""

    nome = serializers.CharField(
        required=False,
        help_text=(
            "Nome da permissão. Quando informado, retorna somente "
            "a permissão correspondente."
        ),
    )
    limite = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=1000,
        default=100,
        help_text=("Quantidade máxima de permissões retornadas. Padrão: 100."),
    )


class RoleAtualizarSerializer(serializers.Serializer):
    """Valida os dados para atualização de uma permissão."""

    novo_nome = serializers.CharField(
        max_length=255,
        required=False,
        help_text="Novo nome da permissão.",
    )
    descricao = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Nova descrição da permissão.",
    )
    atributos = serializers.DictField(
        required=False,
        help_text="Novos atributos da permissão.",
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


class RoleSerializer(serializers.Serializer):
    """Representa uma permissão na resposta da API."""

    id = serializers.CharField(
        allow_null=True,
        help_text="ID interno da permissão no Keycloak.",
    )
    nome = serializers.CharField(
        allow_null=True,
        help_text="Nome da permissão.",
    )
    descricao = serializers.CharField(
        allow_null=True,
        help_text="Descrição da permissão.",
    )
    composite = serializers.BooleanField(
        help_text="Indica se a permissão é composta por outras permissões.",
    )
    container_id = serializers.CharField(
        allow_null=True,
        help_text="ID do container ao qual a permissão pertence.",
    )
    atributos = serializers.DictField(
        help_text="Atributos personalizados da permissão.",
    )
