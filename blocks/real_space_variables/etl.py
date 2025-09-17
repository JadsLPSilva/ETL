# etl.py
from __future__ import annotations
import re
from pathlib import Path
from typing import List
import pandas as pd

from .parser import (
    parse_block,
    parse_numeric_matrix_single,
    parse_numeric_matrix_pair,
    block_is_pair,
)

def _safe_name(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r'[^a-z0-9._-]+', '_', s)
    return s.strip('_') or 'unnamed'

def run_etl(input_path: str, outdir: str, to_parquet: bool = False) -> None:
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)

    blocks = parse_block(input_path)
    if not blocks:
        print(f"[real_space_variables] Nenhum bloco encontrado em: {input_path}")
        return

    per_block_dfs: List[pd.DataFrame] = []

    for header, lines in blocks.items():
        if block_is_pair(lines):
            rows = parse_numeric_matrix_pair(lines)
            if not rows:
                continue
            df = pd.DataFrame(
                rows,
                columns=["i", "j", "value_upup", "err_upup", "value_updn", "err_updn"]
            )
        else:
            rows = parse_numeric_matrix_single(lines)
            if not rows:
                continue
            df = pd.DataFrame(rows, columns=["i", "j", "value", "err"])

            
        df.insert(0, "source_file", Path(input_path).name)

        df.insert(1, "metric", header)

        stem = _safe_name(header)
        per_path = out / f"{stem}.{ 'parquet' if to_parquet else 'csv' }"
        if to_parquet:
            df.to_parquet(per_path, index=False)
        else:
            df.to_csv(per_path, index=False)

        per_block_dfs.append(df)

    if not per_block_dfs:
        print(f"[real_space_variables] Blocos detectados, mas sem linhas numéricas válidas em: {input_path}")
        return

    big = pd.concat(per_block_dfs, ignore_index=True)
    combined = out / f"real_space_variables.{ 'parquet' if to_parquet else 'csv' }"
    if to_parquet:
        big.to_parquet(combined, index=False)
    else:
        big.to_csv(combined, index=False)

    print(f"[real_space_variables] OK: {len(per_block_dfs)} bloco(s) processados.")