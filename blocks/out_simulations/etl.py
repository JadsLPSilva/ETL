from pathlib import Path
from .parser import parse_block

def run_etl(input_path: str, outdir: str, to_parquet: bool = False):
    """
    Executa o ETL do bloco log_simulation:
    - lê o arquivo de entrada
    - aplica parser
    - salva log.* e log_sweeps.* em outdir
    """
    text = Path(input_path).read_text()
    df_header, df_log_sweeps = parse_block(text)

    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    if to_parquet:
        df_header.to_parquet(out / "log.parquet", index=False)
        df_log_sweeps.to_parquet(out / "log_sweeps.parquet", index=False)
    else:
        df_header.to_csv(out / "log.csv", index=False)
        df_log_sweeps.to_csv(out / "log_sweeps.csv", index=False)