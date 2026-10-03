"""Relatorio em Markdown: planta por U, totais e avisos.

Markdown report: rack unit map, totals and warnings.
"""

from __future__ import annotations

from .aviso import Aviso
from .dimensionamento import soma_peso, soma_potencia, soma_u
from .eletrica import circuitos_usados, corrente_por_fase, potencia_por_fase
from .modelo import CapacidadeRack, Equipamento
from .ocupacao import resumo_de_ocupacao
from .termica import temperatura_estimada


def _planta(equipamentos: list[Equipamento], cap: CapacidadeRack) -> list[str]:
    """Linhas da planta, da U mais alta para a mais baixa.

    Plant rows, from the highest rack unit down to the lowest.
    """

    por_u: dict[int, Equipamento] = {}
    for equipamento in sorted(equipamentos, key=lambda item: (item.posicao_u, item.nome)):
        for u in range(equipamento.posicao_u, equipamento.u_final + 1):
            por_u[u] = equipamento
    linhas = [
        "| U | equipamento | categoria | altura_u | peso_kg | consumo_w | fonte |",
        "| --: | --- | --- | --: | --: | --: | --- |",
    ]
    for u in range(cap.altura_u, 0, -1):
        equipamento = por_u.get(u)
        if equipamento is None:
            linhas.append(f"| {u} | - | livre | - | - | - | - |")
        else:
            linhas.append(
                f"| {u} | {equipamento.nome} | {equipamento.categoria} | "
                f"{equipamento.altura_u} | {equipamento.peso_kg:.1f} | "
                f"{equipamento.consumo_w:.0f} | "
                f"{'redundante' if equipamento.fonte_redundante else 'simples'} |"
            )
    return linhas


def gerar_relatorio(
    equipamentos: list[Equipamento],
    cap: CapacidadeRack,
    avisos: list[Aviso],
) -> str:
    """Monta o relatorio completo, deterministico, em PT-BR.

    Builds the full deterministic report, in PT-BR.
    """

    ocupacao = resumo_de_ocupacao(equipamentos, cap)
    graves = [aviso for aviso in avisos if aviso.grave]
    linhas: list[str] = [
        f"# Planta do rack {cap.nome}",
        "",
        "Gerado localmente por `rackplan`. Valores e equipamentos sao ficticios.",
        "Generated locally by `rackplan`. Values and equipment are fictitious.",
        "",
        "## Resumo",
        "",
        f"- Altura do rack: {cap.altura_u}U",
        f"- Altura usada: {soma_u(equipamentos)}U",
        f"- Altura alvo com {cap.folga_recomendada:.0%} de folga: {cap.altura_util_u}U",
        f"- U livres: {ocupacao['u_livres']}",
        f"- Peso total: {soma_peso(equipamentos):.1f} kg de {cap.carga_maxima_kg:.0f} kg",
        f"- Potencia total: {soma_potencia(equipamentos):.0f} W de "
        f"{cap.pdu.potencia_max_w:.0f} W",
        f"- Temperatura de saida estimada: {temperatura_estimada(equipamentos, cap):.1f} C "
        f"(meta {cap.temperatura_max_saida_c:.1f} C, ambiente {cap.temperatura_ambiente_c:.1f} C)",
        "",
        "## Eletrica por fase",
        "",
        "| fase | potencia_w | corrente_a | limite_a |",
        "| --: | --: | --: | --: |",
    ]
    correntes = corrente_por_fase(equipamentos, cap.pdu.tensao_v)
    for fase, watts in potencia_por_fase(equipamentos).items():
        linhas.append(
            f"| {fase} | {watts:.0f} | {correntes.get(fase, 0.0):.1f} | "
            f"{cap.pdu.corrente_max_por_fase_a:.1f} |"
        )
    linhas += [
        "",
        "## Carga por circuito",
        "",
        "| circuito | potencia_w |",
        "| --: | --: |",
    ]
    for circuito, watts in circuitos_usados(equipamentos).items():
        linhas.append(f"| {circuito} | {watts:.0f} |")
    linhas += ["", "## Planta por U", "", *_planta(equipamentos, cap), "", "## Avisos", ""]
    if not avisos:
        linhas.append("nenhum aviso: o rack cabe em altura, peso, potencia e temperatura.")
        linhas.append("No warnings: the rack fits height, weight, power and temperature.")
    else:
        for aviso in avisos:
            linhas.append(f"- {aviso.linha_pt()}")
            linhas.append(f"  - EN: [{aviso.nivel}] {aviso.codigo}: {aviso.en}")
    linhas += [
        "",
        f"Total de avisos: {len(avisos)} ({len(graves)} graves).",
        "",
    ]
    return "\n".join(linhas)


def tem_violacao(avisos: list[Aviso]) -> bool:
    """True quando existe pelo menos um aviso grave.

    True when at least one severe warning exists.
    """

    return any(aviso.grave for aviso in avisos)
