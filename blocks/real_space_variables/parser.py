# parser.py
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Tuple

NUMBER_RE = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?'

# 2 ints + 1 valor (+- err)?
ROW_RE = re.compile(
    rf'^\s*(?P<i>-?\d+)\s+(?P<j>-?\d+)\s+(?P<val>{NUMBER_RE})'
    rf'(?:\s*\+\-\s*(?P<err>{NUMBER_RE}))?\s*$'
)

# 2 ints + (val1 +- err1) + (val2 +- err2)
ROW_PAIR_RE = re.compile(
    rf'^\s*(?P<i>-?\d+)\s+(?P<j>-?\d+)'
    rf'\s+(?P<val1>{NUMBER_RE})\s*\+\-\s*(?P<err1>{NUMBER_RE})'
    rf'\s+(?P<val2>{NUMBER_RE})\s*\+\-\s*(?P<err2>{NUMBER_RE})\s*$'
)

# aceita "… correlation function" (sem (q))
HEADER_CORR_RE = re.compile(
    r'^\s*(?P<name>.+?correlation\s+function)\s*:?\s*(?P<meta>\([^)]+\))?\s*$',
    re.IGNORECASE
)

# aceita qualquer linha com ":" e (opcionalmente) conteúdo após ":" (ex.: "Green's function: ..." ou "density-density correlation fn: (up-up,up-dn)")
HEADER_COLON_RE = re.compile(
    r'^\s*(?P<name>[^:]+):\s*(?P<meta>.*)?$'
)

def _read_lines(input_path: str) -> List[str]:
    return Path(input_path).read_text().splitlines()

def parse_block(input_path: str) -> Dict[str, List[str]]:
    """
    Retorna { header_name : [linhas_de_dados] } para blocos sem '(q)'.
    Um bloco é um cabeçalho seguido de linhas que casam ROW_RE ou ROW_PAIR_RE.
    """
    lines = _read_lines(input_path)
    blocks: Dict[str, List[str]] = {}
    i, n = 0, len(lines)

    def _header_name_if_valid(s: str) -> str | None:
        if "(q)" in s.lower():
            return None
        m_corr = HEADER_CORR_RE.match(s)
        if m_corr:
            return m_corr.group('name').strip()
        m_colon = HEADER_COLON_RE.match(s)
        if m_colon:
            return m_colon.group('name').strip()
        return None

    while i < n:
        name = _header_name_if_valid(lines[i])
        if not name:
            i += 1
            continue

        j = i + 1
        rows: List[str] = []
        # coleta linhas enquanto forem do tipo simples OU par-duplo
        while j < n and (ROW_RE.match(lines[j]) or ROW_PAIR_RE.match(lines[j])):
            rows.append(lines[j])
            j += 1

        if rows:
            blocks.setdefault(name, []).extend(rows)
            i = j
        else:
            i += 1

    return blocks

def parse_numeric_matrix_single(lines: List[str]) -> List[Tuple[int, int, float, float]]:
    """i, j, val, err? (err=nan se ausente)"""
    out: List[Tuple[int, int, float, float]] = []
    for s in lines:
        m = ROW_RE.match(s)
        if not m:
            continue
        i = int(m.group('i')); j = int(m.group('j'))
        val = float(m.group('val'))
        err = float(m.group('err')) if m.group('err') is not None else float('nan')
        out.append((i, j, val, err))
    return out

def parse_numeric_matrix_pair(lines: List[str]) -> List[Tuple[int, int, float, float, float, float]]:
    """i, j, val1, err1, val2, err2 (para up-up / up-dn)"""
    out: List[Tuple[int, int, float, float, float, float]] = []
    for s in lines:
        m = ROW_PAIR_RE.match(s)
        if not m:
            continue
        i = int(m.group('i')); j = int(m.group('j'))
        v1 = float(m.group('val1')); e1 = float(m.group('err1'))
        v2 = float(m.group('val2')); e2 = float(m.group('err2'))
        out.append((i, j, v1, e1, v2, e2))
    return out

def block_is_pair(lines: List[str]) -> bool:
    """Verdadeiro se a maioria das linhas bater o formato 'par-duplo'."""
    hits = sum(1 for s in lines if ROW_PAIR_RE.match(s))
    total = sum(1 for s in lines if (ROW_PAIR_RE.match(s) or ROW_RE.match(s)))
    return (total > 0) and (hits >= max(1, total // 2))