"""CLI do planejador de rack.

Rack planner command line interface.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .aviso import Aviso, formatar
from .dimensionamento import (
    soma_peso,
    soma_potencia,
    soma_u,
    verifica_altura,
    verifica_peso,
    verifica_sobreposicao,
)
from .eletrica import verifica_eletrica
from .modelo import ErroDeValidacao, carregar_capacidade, carregar_equipamentos
from .ocupacao import verificar_folga_entre_fontes
from .relatorio import gerar_relatorio, tem_violacao
from .termica import alertas_de_fluxo, temperatura_estimada, verifica_termica

DESCRICAO = (
    "Planeja o rack de um projeto: U, peso, alimentacao, amperagem e "
    "dissipacao termica, e avisa quando estoura um limite. "
    "Plans a project rack: units, weight, power, current and thermal load."
)


def coletar_avisos(equipamentos, cap) -> list[Aviso]:
    """Reune todos os avisos do planejador em ordem fixa.

    Collects every planner warning in a fixed order.
    """

    avisos: list[Aviso] = []
    avisos.extend(verifica_altura(equipamentos, cap))
    avisos.extend(verifica_peso(equipamentos, cap))
    avisos.extend(verifica_sobreposicao(equipamentos))
    avisos.extend(verifica_eletrica(equipamentos, cap))
    avisos.extend(verifica_termica(equipamentos, cap))
    avisos.extend(verificar_folga_entre_fontes(equipamentos))
    avisos.extend(alertas_de_fluxo(equipamentos, cap))
    return avisos


def construir_parser() -> argparse.ArgumentParser:
    """Monta o parser de argumentos com texto bilingue.

    Builds the argument parser with bilingual help text.
    """

    parser = argparse.ArgumentParser(
        prog="rackplan",
        description=DESCRICAO,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Codigo de saida: 0 sem violacao, 1 com violacao de limite, "
            "2 em erro de entrada.\n"
            "Exit code: 0 no violation, 1 with a limit violation, 2 on bad input."
        ),
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    planejar = sub.add_parser(
        "planejar",
        help="gera a planta do rack em Markdown / generates the rack plan as Markdown",
        description="Gera a planta do rack em Markdown. / Generates the rack plan.",
    )
    planejar.add_argument(
        "equipamentos_pos",
        nargs="?",
        default=None,
        metavar="EQUIPAMENTOS",
        help="YAML dos equipamentos, na forma posicional / equipment YAML, positional",
    )
    planejar.add_argument(
        "--equipamentos",
        "-e",
        dest="equipamentos_opcao",
        default=None,
        help="YAML dos equipamentos (mesma coisa que o posicional) / equipment YAML",
    )
    planejar.add_argument(
        "--capacidade",
        "-c",
        default="dados/capacidade-rack.yaml",
        help="YAML da capacidade do rack / rack capacity YAML (padrao: %(default)s)",
    )
    planejar.add_argument(
        "--saida",
        "-s",
        default=None,
        help="arquivo Markdown de saida / output Markdown file (padrao: stdout)",
    )
    planejar.add_argument(
        "--json",
        action="store_true",
        help="imprime os totais em JSON / prints totals as JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI.

    Command line entry point.
    """

    parser = construir_parser()
    argumentos = parser.parse_args(argv)
    if argumentos.comando != "planejar":  # pragma: no cover - argparse exige subcomando
        parser.error(f"comando desconhecido / unknown command: {argumentos.comando}")
    caminho_equipamentos = (
        argumentos.equipamentos_opcao
        or argumentos.equipamentos_pos
        or "dados/equipamentos-rack.yaml"
    )
    try:
        equipamentos = carregar_equipamentos(caminho_equipamentos)
        capacidade = carregar_capacidade(argumentos.capacidade)
    except ErroDeValidacao as erro:
        print(f"erro de entrada / input error: {erro}", file=sys.stderr)
        return 2
    avisos = coletar_avisos(equipamentos, capacidade)
    relatorio = gerar_relatorio(equipamentos, capacidade, avisos)
    if argumentos.json:
        import json

        print(
            json.dumps(
                {
                    "altura_u": soma_u(equipamentos),
                    "peso_kg": soma_peso(equipamentos),
                    "potencia_w": soma_potencia(equipamentos),
                    "temperatura_saida_c": temperatura_estimada(equipamentos, capacidade),
                    "avisos": [aviso.codigo for aviso in avisos],
                    "violacao": tem_violacao(avisos),
                },
                ensure_ascii=True,
                indent=2,
                sort_keys=True,
            )
        )
    if argumentos.saida:
        destino = Path(argumentos.saida)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(relatorio, encoding="utf-8", newline="\n")
        print(f"planta escrita em {destino.as_posix()} / plan written to {destino.as_posix()}")
    else:
        print(relatorio)
    print(formatar(avisos))
    return 1 if tem_violacao(avisos) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
