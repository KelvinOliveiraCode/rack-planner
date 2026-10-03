"""Modelo de dados do planejador de rack.

Dataclasses do rack, do PDU e do equipamento, com carga e validacao de YAML.
Data model for rack planning: dataclasses plus YAML loading and validation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CATEGORIAS = (
    "switch",
    "roteador",
    "servidor",
    "storage",
    "ups",
    "patch-panel",
    "kvm",
    "organizador",
)

#: Categorias que produzem calor e pedem folga de 1U entre elas.
CATEGORIAS_QUENTES = ("servidor", "storage", "ups")


class ErroDeValidacao(ValueError):
    """Campo invalido no YAML de entrada.

    Invalid field in the input YAML file.
    """


@dataclass(frozen=True)
class Equipamento:
    """Equipamento ficticio que ocupa U no rack.

    Fictitious piece of equipment occupying rack units.
    """

    nome: str
    categoria: str
    altura_u: int
    peso_kg: float
    consumo_w: float
    fonte_redundante: bool
    posicao_u: int
    circuito: int
    fase: int

    @property
    def fonte_de_calor(self) -> bool:
        """True quando o equipamento e uma fonte de calor.

        True when the equipment is a heat source.
        """

        return self.categoria in CATEGORIAS_QUENTES

    @property
    def u_final(self) -> int:
        """Ultima U ocupada, inclusa (U comeca em 1 no rodape).

        Last occupied rack unit, inclusive (units start at 1 at the bottom).
        """

        return self.posicao_u + self.altura_u - 1

    @classmethod
    def de_dict(cls, bruto: dict[str, Any], indice: int) -> "Equipamento":
        """Converte um dicionario YAML em equipamento validado.

        Builds a validated equipment from a YAML mapping.
        """

        obrigatorios = (
            "nome",
            "categoria",
            "altura_u",
            "peso_kg",
            "consumo_w",
            "fonte_redundante",
            "posicao_u",
            "circuito",
            "fase",
        )
        for campo in obrigatorios:
            if campo not in bruto:
                raise ErroDeValidacao(
                    f"equipamento #{indice}: campo obrigatorio ausente: {campo} / "
                    f"equipment #{indice}: missing required field: {campo}"
                )
        altura = bruto["altura_u"]
        posicao = bruto["posicao_u"]
        if not isinstance(altura, int) or altura < 1:
            raise ErroDeValidacao(
                f"{bruto['nome']}: altura_u precisa ser inteiro >= 1 / "
                f"height must be an integer >= 1"
            )
        if not isinstance(posicao, int) or posicao < 1:
            raise ErroDeValidacao(
                f"{bruto['nome']}: posicao_u precisa ser inteiro >= 1 / "
                f"initial position must be an integer >= 1"
            )
        if bruto["categoria"] not in CATEGORIAS:
            raise ErroDeValidacao(
                f"{bruto['nome']}: categoria desconhecida: {bruto['categoria']} / "
                f"unknown category"
            )
        for numerico in ("peso_kg", "consumo_w"):
            valor = bruto[numerico]
            if not isinstance(valor, (int, float)) or isinstance(valor, bool):
                raise ErroDeValidacao(
                    f"{bruto['nome']}: {numerico} precisa ser numero / "
                    f"{numerico} must be a number"
                )
            if valor < 0:
                raise ErroDeValidacao(
                    f"{bruto['nome']}: {numerico} nao pode ser negativo / "
                    f"{numerico} cannot be negative"
                )
        if not isinstance(bruto["fonte_redundante"], bool):
            raise ErroDeValidacao(
                f"{bruto['nome']}: fonte_redundante precisa ser booleano / "
                f"redundant power supply flag must be boolean"
            )
        return cls(
            nome=str(bruto["nome"]),
            categoria=str(bruto["categoria"]),
            altura_u=altura,
            peso_kg=float(bruto["peso_kg"]),
            consumo_w=float(bruto["consumo_w"]),
            fonte_redundante=bool(bruto["fonte_redundante"]),
            posicao_u=posicao,
            circuito=int(bruto["circuito"]),
            fase=int(bruto["fase"]),
        )


@dataclass(frozen=True)
class Pdu:
    """Fonte com_distribuicao de energia do rack.

    Rack power distribution unit.
    """

    nome: str
    tensao_v: float
    circuitos: int
    corrente_por_circuito_a: float
    fases: int
    corrente_max_por_fase_a: float
    potencia_max_w: float

    @classmethod
    def de_dict(cls, bruto: dict[str, Any]) -> "Pdu":
        """Le a PDU do dicionario de capacidade.

        Reads the PDU from the capacity mapping.
        """

        for campo in (
            "nome",
            "tensao_v",
            "circuitos",
            "corrente_por_circuito_a",
            "fases",
            "corrente_max_por_fase_a",
            "potencia_max_w",
        ):
            if campo not in bruto:
                raise ErroDeValidacao(
                    f"pdu: campo obrigatorio ausente: {campo} / "
                    f"pdu: missing required field: {campo}"
                )
        if bruto["circuitos"] < 1 or bruto["fases"] < 1:
            raise ErroDeValidacao(
                "pdu: circuitos e fases precisam ser >= 1 / circuits and phases must be >= 1"
            )
        if bruto["potencia_max_w"] <= 0:
            raise ErroDeValidacao(
                "pdu: potencia_max_w precisa ser > 0 / rated power must be > 0"
            )
        return cls(
            nome=str(bruto["nome"]),
            tensao_v=float(bruto["tensao_v"]),
            circuitos=int(bruto["circuitos"]),
            corrente_por_circuito_a=float(bruto["corrente_por_circuito_a"]),
            fases=int(bruto["fases"]),
            corrente_max_por_fase_a=float(bruto["corrente_max_por_fase_a"]),
            potencia_max_w=float(bruto["potencia_max_w"]),
        )


@dataclass(frozen=True)
class CapacidadeRack:
    """Limites declarados do rack e do ambiente.

    Declared rack and room limits.
    """

    nome: str
    altura_u: int
    carga_maxima_kg: float
    temperatura_ambiente_c: float
    temperatura_max_saida_c: float
    folga_recomendada: float
    pdu: Pdu
    fluxo_ar_m3h: float
    k_termico: float
    categorias_quentes: tuple[str, ...] = field(default=CATEGORIAS_QUENTES)

    @property
    def altura_util_u(self) -> int:
        """Altura alvo depois da folga recomendada de 20%.

        Target height after the recommended 20% headroom.
        """

        return int(math.floor(self.altura_u * (1.0 - self.folga_recomendada)))

    @classmethod
    def de_dict(cls, bruto: dict[str, Any]) -> "CapacidadeRack":
        """Le a capacidade do dicionario YAML.

        Reads the rack capacity from a YAML mapping.
        """

        rack = bruto.get("rack")
        pdu = bruto.get("pdu")
        termica = bruto.get("termica")
        if not isinstance(rack, dict) or not isinstance(pdu, dict) or not isinstance(termica, dict):
            raise ErroDeValidacao(
                "capacidade: as secoes rack, pdu e termica sao obrigatorias / "
                "the rack, pdu and thermals sections are required"
            )
        for campo in (
            "nome",
            "altura_u",
            "carga_maxima_kg",
            "temperatura_ambiente_c",
            "temperatura_max_saida_c",
            "folga_recomendada",
        ):
            if campo not in rack:
                raise ErroDeValidacao(
                    f"capacidade.rack: campo obrigatorio ausente: {campo} / "
                    f"missing required field: {campo}"
                )
        if rack["altura_u"] < 1:
            raise ErroDeValidacao(
                "capacidade.rack: altura_u precisa ser >= 1 / rack height must be >= 1"
            )
        if not 0.0 <= float(rack["folga_recomendada"]) < 0.5:
            raise ErroDeValidacao(
                "capacidade.rack: folga_recomendada precisa estar entre 0 e 0.5 / "
                "recommended headroom must be between 0 and 0.5"
            )
        for campo in ("fluxo_ar_m3h", "k_termico"):
            if campo not in termica:
                raise ErroDeValidacao(
                    f"capacidade.termica: campo obrigatorio ausente: {campo} / "
                    f"missing required field: {campo}"
                )
        if float(termica["fluxo_ar_m3h"]) <= 0:
            raise ErroDeValidacao(
                "capacidade.termica: fluxo_ar_m3h precisa ser > 0 / airflow must be > 0"
            )
        if float(termica["k_termico"]) <= 0:
            raise ErroDeValidacao(
                "capacidade.termica: k_termico precisa ser > 0 / thermal factor must be > 0"
            )
        quentes = tuple(termica.get("categorias_quentes", CATEGORIAS_QUENTES))
        return cls(
            nome=str(rack["nome"]),
            altura_u=int(rack["altura_u"]),
            carga_maxima_kg=float(rack["carga_maxima_kg"]),
            temperatura_ambiente_c=float(rack["temperatura_ambiente_c"]),
            temperatura_max_saida_c=float(rack["temperatura_max_saida_c"]),
            folga_recomendada=float(rack["folga_recomendada"]),
            pdu=Pdu.de_dict(pdu),
            fluxo_ar_m3h=float(termica["fluxo_ar_m3h"]),
            k_termico=float(termica["k_termico"]),
            categorias_quentes=quentes,
        )


def carregar_equipamentos(caminho: str | Path) -> list[Equipamento]:
    """Le a lista de equipamentos do YAML.

    Reads the equipment list from YAML.
    """

    bruto = _ler_yaml(caminho)
    itens = bruto.get("equipamentos")
    if not isinstance(itens, list) or not itens:
        raise ErroDeValidacao(
            "equipamentos: a lista esta vazia ou ausente / equipment list is empty or missing"
        )
    equipamentos = [Equipamento.de_dict(item, indice) for indice, item in enumerate(itens, start=1)]
    nomes = [e.nome for e in equipamentos]
    repetidos = {nome for nome in nomes if nomes.count(nome) > 1}
    if repetidos:
        raise ErroDeValidacao(
            "equipamentos: nomes repetidos: " + ", ".join(sorted(repetidos)) +
            " / duplicate equipment names"
        )
    return equipamentos


def carregar_capacidade(caminho: str | Path) -> CapacidadeRack:
    """Le a capacidade do rack do YAML.

    Reads the rack capacity from YAML.
    """

    return CapacidadeRack.de_dict(_ler_yaml(caminho))


def _ler_yaml(caminho: str | Path) -> dict[str, Any]:
    destino = Path(caminho)
    if not destino.is_file():
        raise ErroDeValidacao(
            f"arquivo nao encontrado: {destino.name} / file not found"
        )
    try:
        bruto = yaml.safe_load(destino.read_text(encoding="utf-8"))
    except yaml.YAMLError as erro:  # pragma: no cover - mensagem de erro do parser
        raise ErroDeValidacao(
            f"YAML invalido: {erro} / invalid YAML file"
        ) from erro
    if not isinstance(bruto, dict):
        raise ErroDeValidacao(
            "a raiz do YAML precisa ser um mapeamento / YAML root must be a mapping"
        )
    return bruto
