import re
from pathlib import Path
from typing import Dict, List, Tuple

Header = re.compile(r'^\s*(?P<name>.+?\(q\))\s*:\s*$')  # ex.: "Bondx(q):"

def parse_block(path: str) -> Dict[str, List[str]]:
    """
    Lê o arquivo .out e captura blocos cujo cabeçalho termina com '(q):',
    acumulando linhas até a próxima linha que contenha ':' (novo cabeçalho).
    Retorna {nome_do_bloco: [linhas_de_dados_str]}.
    """
    lines = Path(path).read_text(encoding='utf-8', errors='ignore').splitlines()

    blocks: Dict[str, List[str]] = {}
    current_name = None
    current_data: List[str] = []

    def flush():
        nonlocal current_name, current_data
        if current_name is not None:
            blocks[current_name] = current_data
        current_name, current_data = None, []

    for ln in lines:
        # Se encontramos um novo cabeçalho (qualquer linha com ':'), checamos se é (q):
        if ':' in ln:
            m = Header.match(ln)
            if m:
                # novo bloco (q): -> descarrega o anterior e começa outro
                flush()
                current_name = m.group('name')
                continue
            else:
                # linha com ':' mas NÃO é "(q):"
                # se já estamos dentro de um bloco (q), isso sinaliza o fim do bloco
                if current_name is not None:
                    flush()
                # fora de bloco, apenas segue
                continue

        # Linha normal de dados
        if current_name is not None:
            # ignora linhas totalmente vazias
            if ln.strip():
                current_data.append(ln.rstrip())

    # arquivo terminou; descarrega último bloco se existir
    flush()
    return blocks

# (opcional) helper para transformar as linhas em tuplas numéricas, se quiser
NumRow = re.compile(r'^\s*(\d+)\s+(\d+)\s+([Ee0-9\.\+\-]+)\s+\+\-\s+([Ee0-9\.\+\-]+)\s*$')

def parse_numeric_matrix(block_lines: List[str]) -> List[Tuple[int, int, float, float]]:
    """
    Converte linhas tipo:
       "0  0   27.6470289502019       +-   0.157368886035319"
    em tuplas (i, j, valor, erro).
    Linhas que não casarem são ignoradas.
    """
    out = []
    for ln in block_lines:
        m = NumRow.match(ln)
        if m:
            kx = int(m.group(1))
            ky = int(m.group(2))
            val = float(m.group(3))
            err = float(m.group(4))
            out.append((kx, ky, val, err))
    return out

if __name__ == "__main__":
    # ajuste o caminho para o seu arquivo .out
    path = "/Users/jlpsilva/Dropbox/SSH/Results/Pining_x_y/bbfieldn0/FIXED_LAMBDA/LAMBDA_fixed_03_NEW/ETL/examples/example.out"
    blocks = parse_block(path)

    # Exemplo de uso: listar os nomes encontrados
    print("Blocos (q) encontrados:", list(blocks.keys()))

    # Pegar especificamente Bondx(q) e converter em matriz numérica
    bondx = blocks.get("Bondx(q)")
    if bondx:
        matriz = parse_numeric_matrix(bondx)
        print("Bondx(q) ->", len(matriz), "linhas numéricas")
        # primeira linha como exemplo
        if matriz:
            print("Exemplo:", matriz[0])