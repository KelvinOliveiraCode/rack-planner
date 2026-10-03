"""Testes da parte eletrica: corrente, fase, circuito e PDU.

Electrical tests: current, phase, circuit and PDU limits.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from rackplan.dimensionamento import soma_potencia
from rackplan.eletrica import (
    circuitos_usados,
    corrente_de_carga,
    corrente_por_fase,
    potencia_por_fase,
    verifica_circuito,
    verifica_corrente_por_fase,
    verifica_eletrica,
    verifica_potencia,
)
from rackplan.modelo import carregar_capacidade, carregar_equipamentos

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


def test_corrente_de_carga() -> None:
    """I = P / V: 2200 W em 127 V da 17,32 A.

    I = P / V: 2200 W at 127 V is 17.32 A.
    """

    assert corrente_de_carga(2200, 127) == pytest.approx(17.32)
    assert corrente_de_carga(0, 127) == 0.0


def test_corrente_recusa_tensao_zero() -> None:
    """Tensao zero e erro explicito, nao divisao por zero.

    Zero voltage raises an explicit error, not a division by zero.
    """

    with pytest.raises(ValueError, match="tensao precisa ser > 0"):
        corrente_de_carga(100, 0)


def test_corrente_recusa_potencia_negativa() -> None:
    """Potencia negativa e erro explicito.

    Negative power raises an explicit error.
    """

    with pytest.raises(ValueError, match="potencia nao pode ser negativa"):
        corrente_de_carga(-1, 127)


def test_corrente_por_fase_plantada(equipamentos) -> None:
    """As tres fases somam 2200, 1200 e 1600 W.

    The three phases sum 2200, 1200 and 1600 W.
    """

    correntes = corrente_por_fase(equipamentos, 127)
    assert set(correntes) == {1, 2, 3}
    assert correntes[1] == pytest.approx(17.32)
    assert correntes[2] == pytest.approx(9.45)
    assert correntes[3] == pytest.approx(12.6)
    assert potencia_por_fase(equipamentos) == {1: 2200.0, 2: 1200.0, 3: 1600.0}
    assert soma_potencia(equipamentos) == pytest.approx(5000.0)


def test_fase_fora_de_faixa_e_erro(equipamentos) -> None:
    """Fase 4 nao existe em instalacao de tres fases.

    Phase 4 does not exist in a three-phase installation.
    """

    quebrado = list(equipamentos)
    quebrado[0] = replace(quebrado[0], fase=4)
    with pytest.raises(ValueError, match="fase 4 fora de 1..3"):
        corrente_por_fase(quebrado, 127)


def test_violacao_de_potencia_plantada(equipamentos, capacidade) -> None:
    """Violacao 3 plantada: 5000 W contra 4800 W de PDU.

    Planted violation 3: 5000 W against a 4800 W PDU.
    """

    avisos = verifica_potencia(equipamentos, capacidade)
    assert [aviso.codigo for aviso in avisos] == ["POTENCIA"]
    assert "5000 W" in avisos[0].pt_br
    assert "200 W" in avisos[0].pt_br


def test_potencia_dentro_do_limite_nao_avisa(equipamentos, capacidade) -> None:
    """Com PDU maior, nao ha aviso de potencia.

    With a larger PDU there is no power warning.
    """

    pdu = replace(capacidade.pdu, potencia_max_w=9000)
    assert verifica_potencia(equipamentos, replace(capacidade, pdu=pdu)) == []


def test_violacao_de_corrente_por_fase_plantada(equipamentos, capacidade) -> None:
    """Violacao 4 plantada: fase 1 a 17,32 A contra 16 A.

    Planted violation 4: phase 1 at 17.32 A against a 16 A limit.
    """

    avisos = verifica_corrente_por_fase(equipamentos, capacidade)
    assert [aviso.codigo for aviso in avisos] == ["CORRENTE_FASE"]
    assert "fase 1" in avisos[0].pt_br
    assert "1.3 A" in avisos[0].pt_br


def test_corrente_de_fase_dentro_do_limite_nao_avisa(equipamentos, capacidade) -> None:
    """Elevando o limite de fase, o aviso some.

    Raising the phase limit removes the warning.
    """

    pdu = replace(capacidade.pdu, corrente_max_por_fase_a=20.0)
    assert verifica_corrente_por_fase(equipamentos, replace(capacidade, pdu=pdu)) == []


def test_circuito_fora_do_pdu_e_erro(equipamentos, capacidade) -> None:
    """Circuito 99 nao existe em PDU de 8 circuitos.

    Circuit 99 does not exist on an 8-circuit PDU.
    """

    quebrado = list(equipamentos)
    quebrado[0] = replace(quebrado[0], circuito=99)
    with pytest.raises(ValueError, match="circuito 99 fora de 1..8"):
        verifica_circuito(quebrado, capacidade)


def test_nenhum_circuito_estoura_no_plantio(equipamentos, capacidade) -> None:
    """A planta distribui os 25 itens em 8 circuitos dentro do nominal.

    The plan spreads 25 items over 8 circuits within the rating.
    """

    carga = circuitos_usados(equipamentos)
    assert len(carga) == 8
    assert max(carga.values()) <= 2032
    assert verifica_circuito(equipamentos, capacidade) == []


def test_verifica_eletrica_reune_os_avisos(equipamentos, capacidade) -> None:
    """A checagem eletrica junta potencia e corrente de fase.

    The electrical check joins power and phase current.
    """

    avisos = verifica_eletrica(equipamentos, capacidade)
    assert [aviso.codigo for aviso in avisos] == ["POTENCIA", "CORRENTE_FASE"]
    assert all(aviso.grave for aviso in avisos)
