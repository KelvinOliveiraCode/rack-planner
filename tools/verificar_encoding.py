"""Confere o encoding dos arquivos de texto do repositorio.

Varre todos os arquivos de texto versionados e recusa BOM UTF-8 no
inicio, caractere de substituicao U+FFFD e ideogramas CJK.

Sai com 0 quando tudo esta limpo e com 1 quando acha problema.
"""

from __future__ import annotations

import sys
from pathlib import Path

#: Raiz do repositorio.
RAIZ = Path(__file__).resolve().parent.parent

#: Extensoes de arquivo de texto varridas.
EXTENSOES = {
    ".py", ".md", ".txt", ".json", ".yml", ".yaml",
    ".toml", ".cfg", ".ini", ".ps1",
}

#: Diretorios ignorados.
IGNORADOS = {".git", "__pycache__", ".pytest_cache", ".coverage"}

#: Binarios ignorados de proposito.
BINARIOS = {".png", ".jpg", ".mp4", ".woff", ".woff2"}

#: Assinatura de BOM UTF-8.
BOM_UTF8 = b"\xef\xbb\xbf"

#: Intervalo de ideogramas CJK.
CJK = range(0x3000, 0x9FFF + 1)

#: Caractere de substituicao.
SUBSTITUICAO = 0xFFFD


def varrer(raiz: Path = RAIZ) -> tuple[list[tuple[str, int, str]], int]:
    """Procura arquivo de texto com encoding invalido.

    Args:
        raiz: Diretorio a varrer.

    Returns:
        Tupla ``(problemas, conferidos)`` em que ``problemas`` e uma
        lista de ``(caminho, linha, motivo)`` e ``conferidos`` e o
        numero de arquivos de texto conferidos.
    """
    problemas: list[tuple[str, int, str]] = []
    conferidos = 0
    for caminho in sorted(raiz.rglob("*")):
        if not caminho.is_file():
            continue
        if any(parte in IGNORADOS for parte in caminho.parts):
            continue
        sufixo = caminho.suffix.lower()
        if sufixo in BINARIOS or sufixo not in EXTENSOES:
            continue
        conferidos += 1
        dados = caminho.read_bytes()
        if dados.startswith(BOM_UTF8):
            problemas.append((
                str(caminho.relative_to(raiz)), 1,
                "BOM UTF-8 no inicio do arquivo",
            ))
        try:
            texto = dados.decode("utf-8")
        except UnicodeDecodeError as exc:
            problemas.append((
                str(caminho.relative_to(raiz)), 0,
                f"nao decodifica como UTF-8: {exc}",
            ))
            continue
        for numero, linha in enumerate(texto.splitlines(), 1):
            for caractere in linha:
                ponto = ord(caractere)
                if ponto == SUBSTITUICAO:
                    problemas.append((
                        str(caminho.relative_to(raiz)), numero,
                        "caractere de substituicao U+FFFD",
                    ))
                    break
                if ponto in CJK:
                    problemas.append((
                        str(caminho.relative_to(raiz)), numero,
                        f"ideograma CJK U+{ponto:04X}",
                    ))
                    break
    return problemas, conferidos


def main() -> int:
    """Executa a varredura e reporta."""
    problemas, conferidos = varrer()
    print(f"conferidos: {conferidos} arquivo(s) de texto")
    if not problemas:
        print("encoding ok: nenhum BOM, nenhum U+FFFD e nenhum CJK")
        return 0
    print(f"encoding FALHOU: {len(problemas)} ocorrencia(s)")
    for caminho, linha, motivo in problemas:
        onde = f"{caminho}:{linha}" if linha else caminho
        print(f"  {onde}: {motivo}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
