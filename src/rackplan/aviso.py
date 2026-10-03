"""Aviso de dimensionamento, em PT-BR e EN.

Dimensioning warning carried in both Portuguese and English.
"""

from __future__ import annotations

from dataclasses import dataclass

GRAVES = ("ALTURA", "PESO", "POTENCIA", "CORRENTE_FASE", "TEMPERATURA", "SOBREPOSICAO_U")
AVISOS = ("FOLGA_U", "FOLGA_PDU", "FONTES_JUNTAS", "FLUXO_AR", "CORRENTE_CIRCUITO")


@dataclass(frozen=True)
class Aviso:
    """Um aviso do planejador: codigo, nivel e texto bilingue.

    A planner warning: code, severity level and bilingual text.
    """

    codigo: str
    nivel: str
    pt_br: str
    en: str
    detalhe: str = ""

    @property
    def grave(self) -> bool:
        """True quando o aviso e uma violacao de limite.

        True when the warning is a limit violation.
        """

        return self.codigo in GRAVES

    def linha_pt(self) -> str:
        """Formata o aviso em uma linha, em PT-BR.

        Formats the warning as a single line in PT-BR.
        """

        return f"[{self.nivel}] {self.codigo}: {self.pt_br}"


def formatar(avisos: list[Aviso]) -> str:
    """Junta os avisos em bloco de texto, na ordem recebida.

    Joins warnings into a text block, keeping the given order.
    """

    if not avisos:
        return "nenhum aviso / no warnings"
    return "\n".join(aviso.linha_pt() for aviso in avisos)
