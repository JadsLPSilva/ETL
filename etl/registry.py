"""
Registry de blocos ETL disponíveis.
Cada bloco expõe uma função `run_etl(input_path, outdir, to_parquet=False)`.
"""

from blocks.out_simulations import run_etl as log_simulation_etl
from blocks.averages import run_etl as log_averages
from blocks.correlations import run_etl as log_correlations
from blocks.k_space_variables import run_etl as log_k_space_variables
from blocks.real_space_variables.etl import run_etl as log_real_space_variables 
REGISTRY = {
    "out_simulations": log_simulation_etl,
    "averages": log_averages,
    "correlations": log_correlations,
    "k_space_variables": log_k_space_variables,
    "real_space_variables": log_real_space_variables,
    # futuramente: "bondq": bondq_etl, "greens": greens_etl, etc.
}

def resolve(block_name: str):
    if block_name not in REGISTRY:
        raise SystemExit(
            f"❌ Bloco desconhecido: {block_name}\n"
            f"Disponíveis: {', '.join(REGISTRY.keys())}"
        )
    return REGISTRY[block_name]