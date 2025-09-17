# etl.py
"""
Executa o ETL dos blocos (q):
- lê o arquivo de entrada (.out)
- aplica o parser para blocos (q) (parser.parse_block)
- salva cada bloco em CSV
"""
from pathlib import Path
import csv
from typing import List, Dict, Tuple

from .parser import parse_block, parse_numeric_matrix


def _sanitize(name: str) -> str:
    """Normaliza o nome do bloco para uso em nome de arquivo."""
    import re
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def run_etl(input_path: str, outdir: str, to_parquet: bool = False):
    """
    Lê o arquivo .out, extrai todos os blocos (q): usando o parser,
    grava um CSV para cada bloco com colunas: filename, block, i, j, value, error.

    Se to_parquet=True, também grava um único arquivo parquet consolidando
    todas as linhas de todos os blocos.
    """
    input_path = str(input_path)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    # Executa o parser: {"Bondx(q)": [linhas], ...}
    blocks: Dict[str, List[str]] = parse_block(input_path)

    all_rows: List[Dict[str, object]] = []
    stem = Path(input_path).stem

    for block_name, lines in blocks.items():
        rows: List[Tuple[int, int, float, float]] = parse_numeric_matrix(lines)

        # Nome do CSV por bloco
        target_csv = out / f"{stem}_{_sanitize(block_name)}.csv"

        # Escreve CSV do bloco
        with target_csv.open("w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["filename", "block", "kx", "ky", "value", "error"]
            )
            writer.writeheader()
            for i, j, val, err in rows:
                rec = {
                    "filename": Path(input_path).name,
                    "block": block_name,
                    "kx": i,
                    "ky": j,
                    "value": val,
                    "error": err,
                }
                writer.writerow(rec)
                all_rows.append(rec)

        print(f"[OK] {len(rows):4d} linhas -> {target_csv}")

    # Opcional: parquet consolidado
    if to_parquet and all_rows:
        try:
            import pandas as pd
        except Exception as e:
            print("[WARN] pandas não disponível; ignorando parquet:", e)
        else:
            df = pd.DataFrame(all_rows)
            out_parquet = out / f"{stem}_kspace_blocks.parquet"
            df.to_parquet(out_parquet, index=False)
            print(f"[OK] parquet salvo em {out_parquet} ({len(df)} linhas)")

    print(f"[OK] Processados {len(blocks)} blocos (q) em '{Path(input_path).name}'.")