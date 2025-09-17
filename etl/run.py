"""
Orquestrador principal do ETL.
Uso via linha de comando:

    python -m etl.run --block log_simulation --input examples/sample_log.txt --outdir outputs

    roda o ETL do bloco desejado, salvando os arquivos em outputs/
"""

import argparse
from pathlib import Path
from .registry import resolve
import subprocess
def main():
    parser = argparse.ArgumentParser(description="ETL Orquestrador de Blocos")
    parser.add_argument("--block", required=True, help="Nome do bloco (ex: log_simulation)")
    parser.add_argument("--input", required=True, help="Arquivo de entrada .out/.log")
    parser.add_argument("--outdir", default="outputs", help="Diretório de saída")
    parser.add_argument("--parquet", action="store_true", help="Salvar em Parquet ao invés de CSV")
    args = parser.parse_args()

    subprocess.run(
        ["bash", str(Path(__file__).parent / "preprocess.sh"), args.input],
        check=True
    )


    runner = resolve(args.block)
    Path(args.outdir).mkdir(parents=True, exist_ok=True)

    print(f"🚀 Rodando ETL para bloco '{args.block}'")
    runner(input_path=args.input, outdir=args.outdir, to_parquet=args.parquet)
    print(f"✅ Arquivos salvos em {args.outdir}")

if __name__ == "__main__":
    main()