# etl.py
"""
Executa o ETL do bloco averages:
- lê o arquivo de entrada (.out)
- aplica o parser (parser.parse)
- salva em CSV
"""

from pathlib import Path
import csv
from .parser import parse_block


def run_etl(input_path: str, outdir: str, to_parquet: bool = False):
    # lê texto do arquivo
    text = Path(input_path).read_text(errors="ignore")
    parsed = parse_block(text)  # retorna dict {"block": "averages", "items": [...]}

    items = parsed.get("items", [])

    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    # nome do arquivo de saída
    out_csv = out / (Path(input_path).stem + "_correlations.csv")

    # escreve CSV
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["filename", "name", "key", "value", "error"]
        )
        writer.writeheader()
        for it in items:
            writer.writerow({
                "filename": Path(input_path).name,
                "name": it.get("name"),
                "key": it.get("key"),
                "value": it.get("value"),
                "error": it.get("error"),
            })

    print(f"[OK] {len(items)} métricas salvas em {out_csv}")

    # opcional: salvar parquet
    if to_parquet:
        import pandas as pd
        df = pd.DataFrame(items)
        out_parquet = out / (Path(input_path).stem + "_correlations.parquet")
        df.to_parquet(out_parquet, index=False)
        print(f"[OK] parquet salvo em {out_parquet}")