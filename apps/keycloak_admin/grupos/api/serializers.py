"""Serializers da API administrativa de grupos."""

from typing import Any

from rest_framework import serializers


class GrupoSerializer(serializers.Serializer):
    """Representa um grupo retornado pela API."""

    id = serializers.CharField(
        read_only=True,
        help_text="ID interno do grupo no Keycloak.",
    )
    nome = serializers.CharField(
        help_text="Nome do grupo.",
    )
    caminho = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Caminho hierárquico do grupo.",
    )
    atributos = serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField(),
        ),
        required=False,
        help_text="Atributos personalizados do grupo.",
    )
    subgrupos = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Subgrupos pertencentes ao grupo.",
    )


class GrupoCriarSerializer(serializers.Serializer):
    """Valida os dados necessários para criação de um grupo."""

    nome = serializers.CharField(
        required=True,
        help_text="Nome do grupo.",
    )
    caminho = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Caminho hierárquico do grupo.",
    )
    atributos = serializers.DictField(
        required=False,
        allow_null=True,
        help_text="Atributos personalizados do grupo.",
    )


class GrupoConsultaSerializer(serializers.Serializer):
    """Valida os parâmetros de consulta de grupos."""

    grupo_id = serializers.CharField(
        required=False,
        help_text=(
            "ID interno do grupo no Keycloak. "
            "Não deve ser utilizado junto com `nome`."
        ),
    )
    nome = serializers.CharField(
        required=False,
        help_text=(
            "Nome ou texto utilizado para pesquisar grupos. "
            "Não deve ser utilizado junto com `grupo_id`."
        ),
    )
    limite = serializers.IntegerField(
        required=False,
        default=100,
        min_value=1,
        max_value=1000,
        help_text=("Quantidade máxima de grupos retornados. Padrão: 100."),
    )

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        """Valida a combinação dos parâmetros de consulta.

        Args:
            attrs: Dados validados pelo serializer.

        Returns:
            Dados validados.

        Raises:
            serializers.ValidationError: Quando mais de um critério
                de identificação é informado.
        """
        if attrs.get("grupo_id") is not None and attrs.get("nome") is not None:
            raise serializers.ValidationError(
                "Informe apenas um critério de consulta: grupo_id ou nome."
            )

        return attrs


class GrupoAtualizarSerializer(serializers.Serializer):
    """Valida os dados para atualização de um grupo."""

    nome = serializers.CharField(
        required=False,
        help_text="Novo nome do grupo.",
    )
    caminho = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Novo caminho hierárquico do grupo.",
    )
    atributos = serializers.DictField(
        required=False,
        allow_null=True,
        help_text="Novos atributos personalizados do grupo.",
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


class GrupoRoleSerializer(serializers.Serializer):
    """Valida os dados de uma operação com Realm Role."""

    nome_permissao = serializers.CharField(
        required=True,
        help_text="Nome da Realm Role.",
    )


class GrupoClientRoleSerializer(serializers.Serializer):
    """Valida os dados de uma operação com Client Role."""

    nome_permissao = serializers.CharField(
        required=True,
        help_text="Nome da Client Role.",
    )
