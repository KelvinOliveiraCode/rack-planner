"""Testes de ocupacao: politica de alocacao e folga entre fontes de calor.

Occupancy tests: allocation policy and clearance between heat sources.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from rackplan.modelo import carregar_capacidade, carregar_equipamentos
from rackplan.ocupacao import (
    alocar,
    ordenar_para_alocar,
    resumo_de_ocupacao,
    verificar_folga_entre_fontes,
)

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture()
def equipamentos() -> list:
    """Lista plantada de 25 equipamentos.

    Planted list of 25 equipment items.
    """

    return carregar_equipamentos(RAIZ / "dados" / "equipamentos-rack.yaml")


@pytest.fixture()
def capacidade():
    """Capacidade plantada do rack de 42U.

    Planted capacity of the 42U rack.
    """

    return carregar_capacidade(RAIZ / "dados" / "capacidade-rack.yaml")


@pytest.fixture()
def rack_amplo(capacidade):
    """Mesmo rack com 60U, o suficiente para o plantio de 50U.

    Same rack with 60 units, enough for the planted 50U.
    """

    return replace(capacidade, altura_u=64)


def unidades(equipamento) -> set[int]:
    """Conjunto de U cobertas por um equipamento.

    Set of rack units covered by one equipment.
    """

    return set(range(equipamento.posicao_u, equipamento.u_final + 1))


def test_ordem_coloca_fonte_antes_e_peso_depois(equipamentos) -> None:
    """A ordem da politica e fonte no fundo, depois peso decrescente.

    The policy order is power supplies first, then weight descending.
    """

    ordem = ordenar_para_alocar(equipamentos)
    fontes = [item for item in ordem if item.fonte_redundante]
    assert fontes, "a planta tem fonte redundante"
    assert all(item.fonte_redundante for item in ordem[: len(fontes)])
    pesos = [item.peso_kg for item in ordem if not item.fonte_redundante]
    assert pesos == sorted(pesos, reverse=True)


def test_alocacao_comeca_no_rodape_e_nao_sobrepoe(equipamentos, rack_amplo) -> None:
    """A politica realoca 25 itens a partir da U 1, sem repetir U.

    The policy reallocates 25 items from U 1, with no repeated unit.
    """

    realocados = alocar(equipamentos, rack_amplo)
    assert realocados[0].posicao_u == 1
    assert [item.posicao_u for item in realocados] == sorted(
        item.posicao_u for item in realocados
    )
    vistas: set[int] = set()
    for item in realocados:
        assert not (vistas & unidades(item)), f"{item.nome} colide com outro item"
        vistas |= unidades(item)
    # 50U de equipamento mais as U de folga entre fontes de calor.
    assert 50 <= len(vistas) <= 50 + len(realocados)
    assert max(vistas) <= 64


def test_alocacao_respeita_folga_entre_fontes_de_calor(equipamentos, rack_amplo) -> None:
    """Duas fontes de calor consecutivas ficam com 1U livre no meio.

    Two consecutive heat sources keep 1U of clearance between them.
    """

    realocados = alocar(equipamentos, rack_amplo)
    for anterior, atual in zip(realocados, realocados[1:]):
        if anterior.fonte_de_calor and atual.fonte_de_calor:
            assert atual.posicao_u >= anterior.u_final + 2


def test_alocacao_recusa_rack_pequeno(equipamentos, capacidade) -> None:
    """Com 42U, a politica diz que nao cabe em vez de Inventar posicao.

    With 42U the policy reports that it does not fit instead of inventing spots.
    """

    with pytest.raises(ValueError, match="nao cabe no rack de 42U"):
        alocar(equipamentos, capacidade)


def test_alocacao_recusa_folga_negativa(equipamentos, rack_amplo) -> None:
    """Folga negativa e erro explicito.

    Negative clearance raises an explicit error.
    """

    with pytest.raises(ValueError, match="nao pode ser negativo"):
        alocar(equipamentos, rack_amplo, folga_entre_fontes_u=-1)


def test_folga_entre_fontes_aponta_no_plantio(equipamentos) -> None:
    """O plano sequencial do README cola fontes de calor, e isso e avisado.

    The sequential plan stacks heat sources together, and it is flagged.
    """

    avisos = verificar_folga_entre_fontes(equipamentos)
    assert [aviso.codigo for aviso in avisos] == ["FONTES_JUNTAS"]
    assert avisos[0].grave is False


def test_sem_colisao_nao_avisa() -> None:
    """Um equipamento so nao gera aviso de folga.

    A single equipment generates no clearance warning.
    """

    lista = carregar_equipamentos(RAIZ / "dados" / "equipamentos-rack.yaml")[:1]
    assert verificar_folga_entre_fontes(lista) == []


def test_resumo_de_ocupacao(equipamentos, capacidade) -> None:
    """O resumo mostra 50U usados em 42U, com folga alvo de 33U.

    The summary shows 50U used in a 42U rack, with a 33U target.
    """

    resumo = resumo_de_ocupacao(equipamentos, capacidade)
    assert resumo == {
        "altura_rack_u": 42,
        "altura_usada_u": 50,
        "altura_util_u": 33,
        "u_livres": 0,
    }
