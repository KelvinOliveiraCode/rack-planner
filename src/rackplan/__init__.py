"""Planejador de rack: altura em U, peso, eletrica, termica e avisos.

Rack planner: rack units, weight, electrical, thermal and warnings.
"""

from __future__ import annotations

from .aviso import Aviso, formatar
from .dimensionamento import (
    soma_peso,
    soma_potencia,
    soma_u,
    u_livres,
    verifica_altura,
    verifica_peso,
    verifica_sobreposicao,
)
from .eletrica import corrente_de_carga, corrente_por_fase, verifica_eletrica
from .modelo import CapacidadeRack, Equipamento, carregar_capacidade, carregar_equipamentos
from .ocupacao import alocar, resumo_de_ocupacao, verificar_folga_entre_fontes
from .relatorio import gerar_relatorio, tem_violacao
from .termica import alertas_de_fluxo, temperatura_estimada, verifica_termica

__all__ = [
    "Aviso",
    "CapacidadeRack",
    "Equipamento",
    "alertas_de_fluxo",
    "alocar",
    "carregar_capacidade",
    "carregar_equipamentos",
    "corrente_de_carga",
    "corrente_por_fase",
    "formatar",
    "gerar_relatorio",
    "resumo_de_ocupacao",
    "soma_peso",
    "soma_potencia",
    "soma_u",
    "temperatura_estimada",
    "tem_violacao",
    "u_livres",
    "verifica_altura",
    "verifica_corrente_por_fase",
    "verifica_eletrica",
    "verifica_peso",
    "verifica_sobreposicao",
    "verifica_termica",
    "verificar_folga_entre_fontes",
]

__version__ = "1.0.0"
