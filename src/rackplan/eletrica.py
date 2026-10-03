"""Parte eletrica: corrente, circuitos, fases e limite do PDU.

Electrical side: current, circuits, phases and PDU limits.
"""

from __future__ import annotations

from .aviso import Aviso
from .dimensionamento import soma_potencia
from .modelo import CapacidadeRack, Equipamento


def corrente_de_carga(potencia_w: float, tensao_v: float) -> float:
    """Converte potencia em corrente: I = P / V.

    Converts power into current: I = P / V.
    """

    if tensao_v <= 0:
        raise ValueError(
            f"tensao precisa ser > 0 V, veio {tensao_v} V / voltage must be > 0 V"
        )
    if potencia_w < 0:
        raise ValueError(
            f"potencia nao pode ser negativa, veio {potencia_w} W / power cannot be negative"
        )
    return round(potencia_w / tensao_v, 2)


def corrente_por_fase(
    equipamentos: list[Equipamento], tensao_v: float
) -> dict[int, float]:
    """Corrente somada em cada fase, em ampere.

    Summed current per phase, in ampere.
    """

    carga: dict[int, float] = {}
    for equipamento in equipamentos:
        if not 1 <= equipamento.fase <= 3:
            raise ValueError(
                f"{equipamento.nome}: fase {equipamento.fase} fora de 1..3 / "
                f"phase out of range"
            )
        carga[equipamento.fase] = round(
            carga.get(equipamento.fase, 0.0) + equipamento.consumo_w, 2
        )
    return {fase: corrente_de_carga(watts, tensao_v) for fase, watts in sorted(carga.items())}


def potencia_por_fase(equipamentos: list[Equipamento]) -> dict[int, float]:
    """Potencia somada em cada fase, em watts.

    Summed power per phase, in watts.
    """

    carga: dict[int, float] = {}
    for equipamento in equipamentos:
        carga[equipamento.fase] = round(
            carga.get(equipamento.fase, 0.0) + equipamento.consumo_w, 2
        )
    return dict(sorted(carga.items()))


def circuitos_usados(equipamentos: list[Equipamento]) -> dict[int, float]:
    """Potencia por circuito, em watts, com o indice ja validado.

    Power per circuit, in watts, with the index validated.
    """

    carga: dict[int, float] = {}
    for equipamento in equipamentos:
        carga[equipamento.circuito] = round(
            carga.get(equipamento.circuito, 0.0) + equipamento.consumo_w, 2
        )
    return dict(sorted(carga.items()))


def verifica_potencia(equipamentos: list[Equipamento], cap: CapacidadeRack) -> list[Aviso]:
    """Compara a potencia total com a potencia nominal do PDU.

    Compares total power against the PDU rated power.
    """

    total = soma_potencia(equipamentos)
    limite = cap.pdu.potencia_max_w
    if total <= limite:
        return []
    return [
        Aviso(
            codigo="POTENCIA",
            nivel="GRAVE",
            pt_br=(
                f"potencia estoura o PDU: {total:.0f} W contra {limite:.0f} W de "
                f"{cap.pdu.nome}, excesso de {total - limite:.0f} W / "
                f"power exceeds the PDU rating"
            ),
            en=(
                f"power exceeds the PDU rating: {total:.0f} W against {limite:.0f} W "
                f"on {cap.pdu.nome}, {total - limite:.0f} W over"
            ),
            detalhe=f"potencia_w={total};potencia_max_w={limite}",
        )
    ]


def verifica_corrente_por_fase(
    equipamentos: list[Equipamento], cap: CapacidadeRack
) -> list[Aviso]:
    """Compara a corrente de cada fase com o limite do PDU.

    Compares each phase current against the PDU limit.
    """

    avisos: list[Aviso] = []
    correntes = corrente_por_fase(equipamentos, cap.pdu.tensao_v)
    for fase, amperes in correntes.items():
        if amperes > cap.pdu.corrente_max_por_fase_a:
            avisos.append(
                Aviso(
                    codigo="CORRENTE_FASE",
                    nivel="GRAVE",
                    pt_br=(
                        f"corrente da fase {fase} estoura: {amperes:.1f} A contra "
                        f"{cap.pdu.corrente_max_por_fase_a:.1f} A, excesso de "
                        f"{amperes - cap.pdu.corrente_max_por_fase_a:.1f} A / "
                        f"phase current overflow"
                    ),
                    en=(
                        f"phase {fase} current overflow: {amperes:.1f} A against "
                        f"{cap.pdu.corrente_max_por_fase_a:.1f} A, "
                        f"{amperes - cap.pdu.corrente_max_por_fase_a:.1f} A over"
                    ),
                    detalhe=f"fase={fase};corrente_a={amperes}",
                )
            )
    return avisos


def verifica_circuito(
    equipamentos: list[Equipamento], cap: CapacidadeRack
) -> list[Aviso]:
    """Compara a corrente de cada circuito com a corrente nominal.

    Compares each circuit current against its rating.
    """

    avisos: list[Aviso] = []
    pdu = cap.pdu
    for circuito, watts in circuitos_usados(equipamentos).items():
        if circuito < 1 or circuito > pdu.circuitos:
            raise ValueError(
                f"circuito {circuito} fora de 1..{pdu.circuitos} do PDU / "
                f"circuit index out of range"
            )
        amperes = corrente_de_carga(watts, pdu.tensao_v)
        if amperes > pdu.corrente_por_circuito_a:
            avisos.append(
                Aviso(
                    codigo="CORRENTE_CIRCUITO",
                    nivel="AVISO",
                    pt_br=(
                        f"circuito {circuito} acima da corrente nominal: "
                        f"{amperes:.1f} A contra {pdu.corrente_por_circuito_a:.1f} A / "
                        f"circuit above rated current"
                    ),
                    en=(
                        f"circuit {circuito} above rated current: {amperes:.1f} A "
                        f"against {pdu.corrente_por_circuito_a:.1f} A"
                    ),
                    detalhe=f"circuito={circuito};potencia_w={watts}",
                )
            )
    return avisos


def verifica_eletrica(equipamentos: list[Equipamento], cap: CapacidadeRack) -> list[Aviso]:
    """Roda todas as verificacoes eletricas, na ordem em que a NF 5410 explica.

    Runs every electrical check, in the order the standard explains them.
    """

    avisos: list[Aviso] = []
    avisos.extend(verifica_potencia(equipamentos, cap))
    avisos.extend(verifica_corrente_por_fase(equipamentos, cap))
    avisos.extend(verifica_circuito(equipamentos, cap))
    return avisos
