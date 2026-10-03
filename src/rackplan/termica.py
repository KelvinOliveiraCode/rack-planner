"""Parte termica: estimativa de temperatura de saida de ar.

Thermal side: estimated outlet air temperature.
"""

from __future__ import annotations

from .aviso import Aviso
from .dimensionamento import soma_potencia
from .modelo import CapacidadeRack, Equipamento


def temperatura_saida(
    potencia_w: float,
    fluxo_ar_m3h: float,
    k_termico: float,
    ambiente_c: float,
) -> float:
    """Temperatura de saida de ar pelo modelo linear adimensional.

    T_saida = T_ambiente + P_W / (k * Q), com Q em m3/h e k em K/(W/(m3/h)).

    Outlet temperature from a linear dimensionless model.
    """

    if potencia_w < 0:
        raise ValueError(
            f"potencia nao pode ser negativa, veio {potencia_w} W / power cannot be negative"
        )
    if fluxo_ar_m3h <= 0:
        raise ValueError(
            f"fluxo de ar precisa ser > 0 m3/h, veio {fluxo_ar_m3h} m3/h / "
            f"airflow must be > 0"
        )
    if k_termico <= 0:
        raise ValueError(
            f"k_termico precisa ser > 0, veio {k_termico} / thermal factor must be > 0"
        )
    return round(ambiente_c + potencia_w / (k_termico * fluxo_ar_m3h), 2)


def temperatura_estimada(equipamentos: list[Equipamento], cap: CapacidadeRack) -> float:
    """Temperatura de saida estimada para o conjunto do rack.

    Estimated outlet temperature for the whole rack.
    """

    return temperatura_saida(
        soma_potencia(equipamentos),
        cap.fluxo_ar_m3h,
        cap.k_termico,
        cap.temperatura_ambiente_c,
    )


def verifica_termica(equipamentos: list[Equipamento], cap: CapacidadeRack) -> list[Aviso]:
    """Compara a temperatura estimada com a meta de saida.

    Compares the estimated temperature against the outlet target.
    """

    estimada = temperatura_estimada(equipamentos, cap)
    if estimada <= cap.temperatura_max_saida_c:
        return []
    return [
        Aviso(
            codigo="TEMPERATURA",
            nivel="GRAVE",
            pt_br=(
                f"temperatura de saida acima da meta: {estimada:.1f} C contra "
                f"{cap.temperatura_max_saida_c:.1f} C com "
                f"{cap.fluxo_ar_m3h:.0f} m3/h de ar / outlet temperature above target"
            ),
            en=(
                f"outlet temperature above target: {estimada:.1f} C against "
                f"{cap.temperatura_max_saida_c:.1f} C at {cap.fluxo_ar_m3h:.0f} m3/h"
            ),
            detalhe=(
                f"temperatura_estimada_c={estimada};"
                f"temperatura_max_saida_c={cap.temperatura_max_saida_c}"
            ),
        )
    ]


def alertas_de_fluxo(equipamentos: list[Equipamento], cap: CapacidadeRack) -> list[Aviso]:
    """Avisa quando o fluxo declarado e pequeno para a potencia instalada.

    Warns when the declared airflow is small for the installed power.
    """

    por_watt = cap.fluxo_ar_m3h / max(soma_potencia(equipamentos), 1e-9)
    if por_watt >= 0.25:
        return []
    return [
        Aviso(
            codigo="FLUXO_AR",
            nivel="AVISO",
            pt_br=(
                f"fluxo de ar apertado: {por_watt:.2f} m3/h por W, abaixo de 0.25 / "
                f"airflow is tight for the installed power"
            ),
            en=(
                f"airflow is tight for the installed power: {por_watt:.2f} m3/h per W, "
                f"below 0.25"
            ),
            detalhe=f"m3h_por_watt={por_watt:.3f}",
        )
    ]
