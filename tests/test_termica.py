"""Testes da parte termica: temperatura de saida e unidades.

Thermal tests: outlet temperature and units.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from rackplan.modelo import carregar_capacidade, carregar_equipamentos
from rackplan.termica import (
    alertas_de_fluxo,
    temperatura_estimada,
    temperatura_saida,
    verifica_termica,
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
    """Capacidade plantada do rack.

    Planted rack capacity.
    """

    return carregar_capacidade(RAIZ / "dados" / "capacidade-rack.yaml")


def test_formula_da_temperatura() -> None:
    """T = ambiente + P / (k * Q): 3150 W com k=0,35 e Q=900 da 14 C de subida.

    T = ambient + P / (k * Q): 3150 W with k=0.35 and Q=900 gives 14 C rise.
    """

    assert temperatura_saida(3150, 900, 0.35, 24) == pytest.approx(34.0)
    assert temperatura_saida(0, 900, 0.35, 24) == pytest.approx(24.0)


def test_fluxo_zero_e_erro() -> None:
    """Fluxo de ar zero nao divide: vira erro explicito.

    Zero airflow does not divide: it raises an explicit error.
    """

    with pytest.raises(ValueError, match="fluxo de ar precisa ser > 0"):
        temperatura_saida(1000, 0, 0.35, 24)


def test_fator_termico_zero_e_erro() -> None:
    """Fator termico zero vira erro explicito.

    Zero thermal factor raises an explicit error.
    """

    with pytest.raises(ValueError, match="k_termico precisa ser > 0"):
        temperatura_saida(1000, 900, 0, 24)


def test_potencia_negativa_e_erro() -> None:
    """Potencia negativa nao faz sentido no modelo.

    Negative power makes no sense in the model.
    """

    with pytest.raises(ValueError, match="potencia nao pode ser negativa"):
        temperatura_saida(-500, 900, 0.35, 24)


def test_temperatura_estimada_do_plantio(equipamentos, capacidade) -> None:
    """5000 W no rack plantado da 39,87 C de saida.

    5000 W in the planted rack gives 39.87 C outlet.
    """

    assert temperatura_estimada(equipamentos, capacidade) == pytest.approx(39.87)


def test_plantio_fica_abaixo_da_meta(equipamentos, capacidade) -> None:
    """O plantio estoura U, peso e potencia, mas nao a temperatura.

    The planted plan overflows units, weight and power, but not temperature.
    """

    assert verifica_termica(equipamentos, capacidade) == []


def test_temperatura_acima_da_meta_avisa(equipamentos, capacidade) -> None:
    """Reduzindo o fluxo de ar para 300 m3/h, a meta de 40 C estoura.

    Dropping airflow to 300 m3/h breaks the 40 C target.
    """

    apertado = replace(capacidade, fluxo_ar_m3h=300)
    avisos = verifica_termica(equipamentos, apertado)
    assert [aviso.codigo for aviso in avisos] == ["TEMPERATURA"]
    assert avisos[0].grave is True
    assert "71.6 C" in avisos[0].pt_br


def test_alerta_de_fluxo_apertado(equipamentos, capacidade) -> None:
    """900 m3/h para 5000 W da 0,18 m3/h por W, abaixo de 0,25.

    900 m3/h for 5000 W is 0.18 m3/h per W, below 0.25.
    """

    avisos = alertas_de_fluxo(equipamentos, capacidade)
    assert [aviso.codigo for aviso in avisos] == ["FLUXO_AR"]
    assert avisos[0].grave is False
    folgado = replace(capacidade, fluxo_ar_m3h=3000)
    assert alertas_de_fluxo(equipamentos, folgado) == []
