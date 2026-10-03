"""Dimensionamento fisico: altura em U, peso e folga.

Physical dimensioning: rack units, weight and headroom.
"""

from __future__ import annotations

from .aviso import Aviso
from .modelo import CapacidadeRack, Equipamento


def soma_u(equipamentos: list[Equipamento]) -> int:
    """Soma das alturas em U dos equipamentos.

    Sums the rack unit height of every equipment.
    """

    return sum(equipamento.altura_u for equipamento in equipamentos)


def soma_peso(equipamentos: list[Equipamento]) -> float:
    """Soma dos pesos, em quilogramas.

    Sums the equipment weights, in kilograms.
    """

    return round(sum(equipamento.peso_kg for equipamento in equipamentos), 2)


def soma_potencia(equipamentos: list[Equipamento]) -> float:
    """Soma das potencias, em watts.

    Sums the equipment power draw, in watts.
    """

    return round(sum(equipamento.consumo_w for equipamento in equipamentos), 2)


def u_ocupadas(equipamentos: list[Equipamento]) -> set[int]:
    """Conjunto de U cobertas por pelo menos um equipamento.

    Set of rack units covered by at least one equipment.
    """

    unidades: set[int] = set()
    for equipamento in equipamentos:
        unidades.update(range(equipamento.posicao_u, equipamento.u_final + 1))
    return unidades


def u_livres(equipamentos: list[Equipamento], altura_u: int) -> list[int]:
    """Lista ordenada de U livres dentro da altura do rack.

    Sorted list of free rack units within the rack height.
    """

    ocupadas = u_ocupadas(equipamentos)
    return [u for u in range(1, altura_u + 1) if u not in ocupadas]


def sobreposicoes(equipamentos: list[Equipamento]) -> list[str]:
    """Nomes dos equipamentos que dividem a mesma U.

    Names of the equipment items sharing the same rack unit.
    """

    dono: dict[int, str] = {}
    conflitos: list[str] = []
    for equipamento in sorted(equipamentos, key=lambda item: (item.posicao_u, item.nome)):
        for u in range(equipamento.posicao_u, equipamento.u_final + 1):
            if u in dono and dono[u] != equipamento.nome:
                par = f"{dono[u]} x {equipamento.nome}"
                if par not in conflitos:
                    conflitos.append(par)
            dono[u] = equipamento.nome
    return conflitos


def verifica_altura(equipamentos: list[Equipamento], cap: CapacidadeRack) -> list[Aviso]:
    """Compara a soma de U com a altura do rack e com a folga recomendada.

    Compares the total rack units against rack height and recommended headroom.
    """

    avisos: list[Aviso] = []
    total = soma_u(equipamentos)
    if total > cap.altura_u:
        avisos.append(
            Aviso(
                codigo="ALTURA",
                nivel="GRAVE",
                pt_br=(
                    f"altura estoura: {total}U em rack de {cap.altura_u}U "
                    f"({total - cap.altura_u}U acima do rack) / height overflow"
                ),
                en=(
                    f"height overflow: {total}U in a {cap.altura_u}U rack "
                    f"({total - cap.altura_u}U over the rack)"
                ),
                detalhe=f"altura_usada_u={total};altura_rack_u={cap.altura_u}",
            )
        )
    elif total > cap.altura_util_u:
        avisos.append(
            Aviso(
                codigo="FOLGA_U",
                nivel="AVISO",
                pt_br=(
                    f"folga de U comprometida: {total}U usados, recomendado ate "
                    f"{cap.altura_util_u}U com {cap.folga_recomendada:.0%} de folga / "
                    f"rack unit headroom is thin"
                ),
                en=(
                    f"rack unit headroom is thin: {total}U used, "
                    f"{cap.altura_util_u}U recommended with "
                    f"{cap.folga_recomendada:.0%} headroom"
                ),
                detalhe=f"altura_usada_u={total};altura_util_u={cap.altura_util_u}",
            )
        )
    return avisos


def verifica_peso(equipamentos: list[Equipamento], cap: CapacidadeRack) -> list[Aviso]:
    """Compara o peso total com a carga maxima do rack.

    Compares total weight against the rack load rating.
    """

    total = soma_peso(equipamentos)
    if total <= cap.carga_maxima_kg:
        return []
    return [
        Aviso(
            codigo="PESO",
            nivel="GRAVE",
            pt_br=(
                f"peso estoura: {total:.1f} kg contra carga maxima de "
                f"{cap.carga_maxima_kg:.0f} kg, excesso de "
                f"{total - cap.carga_maxima_kg:.1f} kg / weight overflow"
            ),
            en=(
                f"weight overflow: {total:.1f} kg against a "
                f"{cap.carga_maxima_kg:.0f} kg rating, "
                f"{total - cap.carga_maxima_kg:.1f} kg over"
            ),
            detalhe=f"peso_kg={total};carga_maxima_kg={cap.carga_maxima_kg}",
        )
    ]


def verifica_sobreposicao(equipamentos: list[Equipamento]) -> list[Aviso]:
    """Aponta equipamentos que dividem a mesma U.

    Flags equipment items that share the same rack unit.
    """

    conflitos = sobreposicoes(equipamentos)
    if not conflitos:
        return []
    lista = ", ".join(conflitos)
    return [
        Aviso(
            codigo="SOBREPOSICAO_U",
            nivel="GRAVE",
            pt_br=f"posicoes em U se sobrepoem: {lista} / rack unit overlap",
            en=f"rack unit positions overlap: {lista}",
            detalhe=f"pares={len(conflitos)}",
        )
    ]
