"""Testes de dimensionamento: U, peso, folga e carga de YAML.

Dimensioning tests: rack units, weight, headroom and YAML loading.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from rackplan.dimensionamento import (
    soma_peso,
    soma_potencia,
    soma_u,
    sobreposicoes,
    u_livres,
    u_ocupadas,
    verifica_altura,
    verifica_peso,
    verifica_sobreposicao,
)
from rackplan.modelo import (
    CapacidadeRack,
    ErroDeValidacao,
    carregar_capacidade,
    carregar_equipamentos,
)

RAIZ = Path(__file__).resolve().parent.parent
EQUIPAMENTOS = RAIZ / "dados" / "equipamentos-rack.yaml"
CAPACIDADE = RAIZ / "dados" / "capacidade-rack.yaml"


@pytest.fixture()
def equipamentos() -> list:
    """Lista plantada de 25 equipamentos.

    Planted list of 25 equipment items.
    """

    return carregar_equipamentos(EQUIPAMENTOS)


@pytest.fixture()
def capacidade() -> CapacidadeRack:
    """Capacidade plantada do rack de 42U.

    Planted capacity of the 42U rack.
    """

    return carregar_capacidade(CAPACIDADE)


def test_totais_do_plantio(equipamentos, capacidade) -> None:
    """O conjunto plantado soma 50U, 430,2 kg e 5000 W.

    The planted set sums 50U, 430.2 kg and 5000 W.
    """

    assert len(equipamentos) == 25
    assert soma_u(equipamentos) == 50
    assert soma_peso(equipamentos) == pytest.approx(430.2)
    assert soma_potencia(equipamentos) == pytest.approx(5000.0)
    assert capacidade.altura_u == 42
    assert capacidade.altura_util_u == 33


def test_violacao_de_altura_plantada(equipamentos, capacidade) -> None:
    """Violacao 1 plantada: 50U em rack de 42U.

    Planted violation 1: 50U in a 42U rack.
    """

    avisos = verifica_altura(equipamentos, capacidade)
    assert [aviso.codigo for aviso in avisos] == ["ALTURA"]
    assert avisos[0].grave is True
    assert "50U" in avisos[0].pt_br
    assert "8U" in avisos[0].pt_br


def test_folga_de_u_avisa_sem_estourar(equipamentos) -> None:
    """Sem estourar a altura, o aviso passa a ser de folga.

    Without overflowing, the warning becomes a headroom warning.
    """

    capacidade = CapacidadeRack(
        nome="rack-teste",
        altura_u=60,
        carga_maxima_kg=900,
        temperatura_ambiente_c=24,
        temperatura_max_saida_c=40,
        folga_recomendada=0.2,
        pdu=carregar_capacidade(CAPACIDADE).pdu,
        fluxo_ar_m3h=900,
        k_termico=0.35,
    )
    avisos = verifica_altura(equipamentos, capacidade)
    assert [aviso.codigo for aviso in avisos] == ["FOLGA_U"]
    assert avisos[0].grave is False


def test_violacao_de_peso_plantada(equipamentos, capacidade) -> None:
    """Violacao 2 plantada: 430,2 kg contra 400 kg de carga maxima.

    Planted violation 2: 430.2 kg against a 400 kg rating.
    """

    avisos = verifica_peso(equipamentos, capacidade)
    assert [aviso.codigo for aviso in avisos] == ["PESO"]
    assert "430.2 kg" in avisos[0].pt_br
    assert "30.2 kg" in avisos[0].pt_br


def test_peso_dentro_do_limite_nao_avisa(equipamentos, capacidade) -> None:
    """Com carga maxima alta, nao ha aviso de peso.

    With a higher load rating there is no weight warning.
    """

    from dataclasses import replace

    assert verifica_peso(equipamentos, replace(capacidade, carga_maxima_kg=800)) == []


def test_u_livres_e_ocupadas(equipamentos, capacidade) -> None:
    """As U ocupadas formam o intervalo 1..50 e nao cabem em 42U.

    Occupied units span 1..50 and do not fit in 42U.
    """

    ocupadas = u_ocupadas(equipamentos)
    assert min(ocupadas) == 1
    assert max(ocupadas) == 50
    assert len(ocupadas) == 50
    assert u_livres(equipamentos, capacidade.altura_u) == []


def test_sobreposicao_detectada_quando_o_plano_repete_u(equipamentos) -> None:
    """Dois itens na mesma U sao apontados como sobreposicao.

    Two items sharing a unit are flagged as an overlap.
    """

    from dataclasses import replace

    colidindo = list(equipamentos)
    colidindo[1] = replace(colidindo[1], posicao_u=equipamentos[0].posicao_u)
    conflitos = sobreposicoes(colidindo)
    assert conflitos and "x" in conflitos[0]
    avisos = verifica_sobreposicao(colidindo)
    assert avisos[0].codigo == "SOBREPOSICAO_U"
    assert avisos[0].grave is True


def test_plantio_sequencial_nao_sobrepoe(equipamentos) -> None:
    """O plano do gerador e sequencial: estoura a altura, mas nao repete U.

    The generated plan is sequential: it overflows the height without repeating units.
    """

    assert sobreposicoes(equipamentos) == []
    assert verifica_sobreposicao(equipamentos) == []


def test_sem_sobreposicao_nao_avisa(capacidade) -> None:
    """Um unico equipamento no rodape nao gera sobreposicao.

    A single item at the bottom generates no overlap.
    """

    lista = carregar_equipamentos(EQUIPAMENTOS)[:1]
    assert verifica_sobreposicao(lista) == []


def test_yaml_de_equipamento_invalido(tmp_path) -> None:
    """Campo obrigatorio ausente vira erro bilingue.

    A missing required field becomes a bilingual error.
    """

    arquivo = tmp_path / "ruim.yaml"
    arquivo.write_text(
        "equipamentos:\n  - nome: x\n    categoria: switch\n", encoding="utf-8"
    )
    with pytest.raises(ErroDeValidacao) as erro:
        carregar_equipamentos(arquivo)
    assert "campo obrigatorio ausente" in str(erro.value)
    assert "missing required field" in str(erro.value)


def test_nome_repetido_e_rejeitado(tmp_path) -> None:
    """Nome repetido invalida a lista inteira.

    A duplicated name invalidates the whole list.
    """

    item = (
        "  - nome: {nome}\n    categoria: switch\n    altura_u: 1\n    peso_kg: 1\n"
        "    consumo_w: 1\n    fonte_redundante: false\n    posicao_u: {posicao}\n"
        "    circuito: 1\n    fase: 1\n"
    )
    arquivo = tmp_path / "dup.yaml"
    arquivo.write_text(
        "equipamentos:\n"
        + item.format(nome="dup", posicao=1)
        + item.format(nome="dup", posicao=2),
        encoding="utf-8",
    )
    with pytest.raises(ErroDeValidacao, match="nomes repetidos"):
        carregar_equipamentos(arquivo)


def test_valores_invalidos_sao_rejeitados(tmp_path) -> None:
    """Altura 0, peso negativo e categoria desconhecida sao recusados.

    Height 0, negative weight and unknown category are rejected.
    """

    base = (
        "equipamentos:\n  - nome: {nome}\n    categoria: {categoria}\n"
        "    altura_u: {altura}\n    peso_kg: {peso}\n    consumo_w: 10\n"
        "    fonte_redundante: false\n    posicao_u: 1\n    circuito: 1\n    fase: 1\n"
    )
    casos = (
        ({"nome": "a", "categoria": "switch", "altura": 0, "peso": 1}, "altura_u"),
        ({"nome": "b", "categoria": "switch", "altura": 1, "peso": -3}, "nao pode ser negativo"),
        ({"nome": "c", "categoria": "teapot", "altura": 1, "peso": 1}, "categoria desconhecida"),
    )
    for indice, (campos, esperado) in enumerate(casos):
        arquivo = tmp_path / f"caso{indice}.yaml"
        arquivo.write_text(base.format(**campos), encoding="utf-8")
        with pytest.raises(ErroDeValidacao, match=esperado):
            carregar_equipamentos(arquivo)


def test_arquivo_ausente_e_erro_traduzido(tmp_path) -> None:
    """Arquivo inexistente vira erro com o nome do arquivo.

    A missing file becomes an error naming the file.
    """

    with pytest.raises(ErroDeValidacao, match="file not found"):
        carregar_equipamentos(tmp_path / "nao-existe.yaml")


def test_lista_vazia_e_rejeitada(tmp_path) -> None:
    """Lista vazia e recusada.

    An empty list is rejected.
    """

    arquivo = tmp_path / "vazio.yaml"
    arquivo.write_text("equipamentos: []\n", encoding="utf-8")
    with pytest.raises(ErroDeValidacao, match="vazia"):
        carregar_equipamentos(arquivo)


def test_capacidade_sem_secoes_obrigatorias(tmp_path) -> None:
    """Capacidade sem as secoes rack, pdu e termica e recusada.

    A capacity file without the required sections is rejected.
    """

    arquivo = tmp_path / "cap.yaml"
    arquivo.write_text("rack: {}\n", encoding="utf-8")
    with pytest.raises(ErroDeValidacao, match="secoes rack, pdu e termica"):
        carregar_capacidade(arquivo)


def test_capacidade_com_valores_fora_de_faixa(tmp_path) -> None:
    """Folga de 50% e fluxo zero sao recusados.

    50% headroom and zero airflow are rejected.
    """

    corpo = (
        "rack:\n  nome: r\n  altura_u: 42\n  carga_maxima_kg: 400\n"
        "  temperatura_ambiente_c: 24\n  temperatura_max_saida_c: 40\n"
        "  folga_recomendada: {folga}\n"
        "pdu:\n  nome: p\n  tensao_v: 127\n  circuitos: 8\n"
        "  corrente_por_circuito_a: 16\n  fases: 3\n  corrente_max_por_fase_a: 16\n"
        "  potencia_max_w: 4800\n"
        "termica:\n  fluxo_ar_m3h: {fluxo}\n  k_termico: 0.35\n"
    )
    for indice, (folga, fluxo, esperado) in enumerate(
        ((0.6, 900, "folga_recomendada"), (0.2, 0, "fluxo_ar_m3h"))
    ):
        arquivo = tmp_path / f"cap{indice}.yaml"
        arquivo.write_text(corpo.format(folga=folga, fluxo=fluxo), encoding="utf-8")
        with pytest.raises(ErroDeValidacao, match=esperado):
            carregar_capacidade(arquivo)
