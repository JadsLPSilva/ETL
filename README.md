# ETL para Blocos `.log simulation`

Este módulo implementa um pipeline **ETL (Extract → Transform → Load)** para logs de simulação
do tipo:

tausk=         200
phonskip=           2
…
Finished measurement sweep         4000
…
Accept2 SSH=  0.1767841
Accept2 Hol.= 1.000000

---

## 🔹 Estrutura

- **Extract**  
  - Identifica e extrai parâmetros escalares (ex.: `tausk`, `phonskip`, `lambda0`, `mu`, `gamma`, etc.).
  - Separa blocos de sweeps contendo métricas (`asgn`, `accept_holstein`, `redo_ratio`, `nwrap`, `torth`).

- **Transform**  
  - Converte valores para tipos numéricos (`int`, `float`, notação científica).
  - Normaliza nomes (`snake_case`).
  - Gera duas tabelas:  
    1. `run_header` → parâmetros globais da simulação  
    2. `sweeps` → evolução das métricas por sweep

- **Load**  
  - Salva resultados em `.csv` ou `.parquet`.  
  - Pode ser integrado ao **DuckDB** ou **pandas** para análises posteriores.

---

## 🔹 Uso

```bash
# Instalar dependências

# (opcional) criar ambiente
python -m venv .venv && source .venv/bin/activate

# instalar
pip install -r requirements.txt

# Rodar ETL em um arquivo de log
python3 -m etl.run --block k_space_variables --input examples/example.out --outdir outputs --parquet

## --parquet é uma flag