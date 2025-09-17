"""
Blocos:s
Expõe: parse_block (parser) e run_etl (cola ETL para salvar em arquivos).
"""
from .parser import parse_block
from .etl import run_etl

__all__ = ["parse_block", "run_etl"]


## __all_ : define o que vai ser exportado quando fizer from blocks.out_simulations import *