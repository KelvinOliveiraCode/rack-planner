"""Ocupacao de U: politica de alocacao e conferencia de posicao.

Rack unit occupancy: allocation policy and position checks.
"""

from __future__ import annotations

from dataclasses import replace

from .aviso import Aviso
from .dimensionamento import soma_u, u_livres
from .modelo import CapacidadeRack, Equipamento


def ordenar_para_alocar(equipamentos: list[Equipamento]) -> list[Equipamento]:
    """Ordem de alocacao: fonte no fundo, depois peso descendente, depois nome.

    Allocation order: power supplies at the rear, then weight descending.
    """

    return sorted(
        equipamentos,
        key=lambda item: (
            0 if item.fonte_redundante else 1,
            -item.peso_kg,
            item.nome,
        ),
    )


def alocar(
    equipamentos: list[Equipamento],
    cap: CapacidadeRack,
    folga_entre_fontes_u: int = 1,
) -> list[Equipamento]:
    """Realoca os equipamentos a partir da politica do projeto.

    Reallocates equipment from the project policy: heaviest at the bottom,
    redundant power supplies at the rear, and 1U of clearance between heat
    sources.
    """

    if folga_entre_fontes_u < 0:
        raise ValueError(
            f"folga_entre_fontes_u nao pode ser negativo / clearance cannot be negative"
        )
    ocupadas: list[int] = []
    resultado: list[Equipamento] = []
    anterior_fonte_de_calor = False
    for equipamento in ordenar_para_alocar(equipamentos):
        if anterior_fonte_de_calor and equipamento.fonte_de_calor and folga_entre_fontes_u:
            # 1U livre entre duas fontes de calor consecutivas.
            ocupadas.extend(range(len(ocupadas), len(ocupadas) + folga_entre_fontes_u))
        inicio = len(ocupadas) + 1
        ocupadas.extend(range(inicio, inicio + equipamento.altura_u))
        resultado.append(replace(equipamento, posicao_u=inicio))
        anterior_fonte_de_calor = equipamento.fonte_de_calor
    estourou = [item.nome for item in resultado if item.u_final > cap.altura_u]
    if estourou:
        raise ValueError(
            f"nao cabe no rack de {cap.altura_u}U: {', '.join(estourou)} / "
            f"the equipment does not fit in the rack"
        )
    return sorted(resultado, key=lambda item: item.posicao_u)


def verificar_folga_entre_fontes(
    equipamentos: list[Equipamento], folga_u: int = 1
) -> list[Aviso]:
    """Aponta fontes de calor coladas sem a folga de 1U.

    Flags heat sources stacked without the 1U clearance.
    """

    ordenados = sorted(equipamentos, key=lambda item: (item.posicao_u, item.nome))
    problemas: list[str] = []
    for anterior, atual in zip(ordenados, ordenados[1:]):
        if anterior.fonte_de_calor and atual.fonte_de_calor:
            if atual.posicao_u <= anterior.u_final:
                problemas.append(f"{anterior.nome} x {atual.nome} (sobrepostos)")
            elif atual.posicao_u - anterior.u_final <= folga_u:
                problemas.append(f"{anterior.nome} x {atual.nome} (sem folga de {folga_u}U)")
    if not problemas:
        return []
    lista = ", ".join(problemas)
    return [
        Aviso(
            codigo="FONTES_JUNTAS",
            nivel="AVISO",
            pt_br=(
                f"fontes de calor sem folga de {folga_u}U entre elas: {lista} / "
                f"heat sources without clearance"
            ),
            en=f"heat sources without {folga_u}U clearance: {lista}",
            detalhe=f"pares={len(problemas)}",
        )
    ]


def resumo_de_ocupacao(equipamentos: list[Equipamento], cap: CapacidadeRack) -> dict[str, int]:
    """Numeros de ocupacao para o relatorio: U usadas, livres e folga.

    Occupancy numbers for the report: units used, free and headroom.
    """

    livres = u_livres(equipamentos, cap.altura_u)
    return {
        "altura_rack_u": cap.altura_u,
        "altura_usada_u": soma_u(equipamentos),
        "altura_util_u": cap.altura_util_u,
        "u_livres": len(livres),
    }
