"""Testes da CLI: codigo de saida, arquivo gerado e determinismo.

CLI tests: exit codes, generated file and determinism.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rackplan.aviso import formatar
from rackplan.cli import coletar_avisos, main
from rackplan.modelo import carregar_capacidade, carregar_equipamentos
from rackplan.relatorio import gerar_relatorio, tem_violacao

RAIZ = Path(__file__).resolve().parent.parent
EQUIPAMENTOS = RAIZ / "dados" / "equipamentos-rack.yaml"
CAPACIDADE = RAIZ / "dados" / "capacidade-rack.yaml"

GRAVES_PLANTADOS = ("ALTURA", "PESO", "POTENCIA", "CORRENTE_FASE")


def test_help_abre_sem_erro() -> None:
    """--help mostra o texto bilingue e sai com 0.

    --help prints the bilingual text and exits with 0.
    """

    with pytest.raises(SystemExit) as saida:
        main(["--help"])
    assert saida.value.code == 0


def test_sem_subcomando_e_erro_de_uso() -> None:
    """Sem subcomando, argparse aborta com codigo 2.

    Without a subcommand argparse aborts with code 2.
    """

    with pytest.raises(SystemExit) as saida:
        main([])
    assert saida.value.code == 2


def test_ajuda_do_subcomando_planejar() -> None:
    """O subcomando planejar documenta a saida 0/1/2.

    The plan subcommand documents the 0/1/2 exit code.
    """

    with pytest.raises(SystemExit) as saida:
        main(["planejar", "--help"])
    assert saida.value.code == 0


def test_planejar_aponta_as_quatro_violacoes(tmp_path, capsys) -> None:
    """O comando do README acusa as 4 violacoes plantadas e sai com 1.

    The README command reports the 4 planted violations and exits with 1.
    """

    destino = tmp_path / "planta-rack.md"
    codigo = main(
        [
            "planejar",
            "--equipamentos",
            str(EQUIPAMENTOS),
            "--capacidade",
            str(CAPACIDADE),
            "--saida",
            str(destino),
        ]
    )
    assert codigo == 1
    texto = destino.read_text(encoding="utf-8")
    for violacao in GRAVES_PLANTADOS:
        assert violacao in texto, violacao
    assert "50U" in texto
    assert "430.2 kg" in texto
    assert "5000 W" in texto
    assert "17.3 A" in texto
    assert "39.9 C" in texto
    assert "planta escrita em" in capsys.readouterr().out


def test_planta_mostra_cada_u_ocupada() -> None:
    """A planta lista as 42U do rack, marking ocupadas e livres.

    The plan lists all 42 rack units, marking occupied and free ones.
    """

    equipamentos = carregar_equipamentos(EQUIPAMENTOS)
    capacidade = carregar_capacidade(CAPACIDADE)
    texto = gerar_relatorio(equipamentos, capacidade, coletar_avisos(equipamentos, capacidade))
    planta = texto.split("## Planta por U", 1)[1].split("## Avisos", 1)[0]
    linhas = [linha for linha in planta.splitlines() if linha.startswith("|")]
    unidades = [linha for linha in linhas[2:] if linha.split("|")[1].strip().isdigit()]
    assert len(unidades) == 42
    assert "| 1 | patch-panel-48p |" in planta
    assert "| 42 |" in planta
    # com 50U em 42U nao sobra U livre: e exatamente isso que a viola��ao ALTURA avisa
    assert "livre" not in planta


def test_saida_e_deterministica(tmp_path) -> None:
    """Duas execucoes com os mesmos dados geram o mesmo arquivo.

    Two runs with the same data generate the same file.
    """

    destinos = []
    for nome in ("primeira.md", "segunda.md"):
        destino = tmp_path / nome
        main(
            [
                "planejar",
                "--equipamentos",
                str(EQUIPAMENTOS),
                "--capacidade",
                str(CAPACIDADE),
                "--saida",
                str(destino),
            ]
        )
        destinos.append(destino.read_text(encoding="utf-8"))
    assert destinos[0] == destinos[1]


def test_json_mostra_totais_e_violacao(tmp_path, capsys) -> None:
    """A opcao --json imprime os totais e a flag de violacao.

    The --json option prints the totals and the violation flag.
    """

    codigo = main(
        [
            "planejar",
            "--equipamentos",
            str(EQUIPAMENTOS),
            "--capacidade",
            str(CAPACIDADE),
            "--json",
        ]
    )
    assert codigo == 1
    saida = capsys.readouterr().out
    bloco = saida[saida.index("{") : saida.index("}") + 1]
    dados = json.loads(bloco)
    assert dados["altura_u"] == 50
    assert dados["peso_kg"] == pytest.approx(430.2)
    assert dados["potencia_w"] == pytest.approx(5000.0)
    assert dados["temperatura_saida_c"] == pytest.approx(39.87)
    assert dados["violacao"] is True
    assert set(GRAVES_PLANTADOS) <= set(dados["avisos"])


def test_arquivo_inexistente_saida_2(capsys) -> None:
    """Entrada invalida sai com 2 e mensagem bilingue no stderr.

    Invalid input exits with 2 and a bilingual message on stderr.
    """

    codigo = main(
        [
            "planejar",
            "--equipamentos",
            "dados/nao-existe.yaml",
            "--capacidade",
            str(CAPACIDADE),
        ]
    )
    assert codigo == 2
    assert "input error" in capsys.readouterr().err


def test_sem_violacao_sai_com_zero(tmp_path) -> None:
    """Um rack de 42U com 5 itens nao gera violacao e sai com 0.

    A 42U rack with 5 items raises no violation and exits with 0.
    """

    cinco = tmp_path / "cinco.yaml"
    linhas = ["equipamentos:"]
    for indice in range(5):
        linhas += [
            f"  - nome: item-{indice}",
            "    categoria: patch-panel",
            "    altura_u: 1",
            "    peso_kg: 2.0",
            "    consumo_w: 0",
            "    fonte_redundante: false",
            f"    posicao_u: {indice + 1}",
            "    circuito: 1",
            "    fase: 1",
        ]
    cinco.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    destino = tmp_path / "limpo.md"
    codigo = main(
        [
            "planejar",
            "--equipamentos",
            str(cinco),
            "--capacidade",
            str(CAPACIDADE),
            "--saida",
            str(destino),
        ]
    )
    assert codigo == 0
    texto = destino.read_text(encoding="utf-8")
    assert "nenhum aviso" in texto
    assert "| 42 | - | livre |" in texto
    assert texto.count("| livre |") == 37


def test_formatar_de_avisos() -> None:
    """A lista vazia de avisos vira texto explicito.

    An empty warning list becomes explicit text.
    """

    assert formatar([]) == "nenhum aviso / no warnings"
    equipamentos = carregar_equipamentos(EQUIPAMENTOS)
    capacidade = carregar_capacidade(CAPACIDADE)
    avisos = coletar_avisos(equipamentos, capacidade)
    assert formatar(avisos).startswith("[GRAVE] ALTURA:")
    assert tem_violacao(avisos) is True
