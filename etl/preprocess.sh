#!/bin/bash
# preprocess.sh
# Normaliza cabeçalhos "bonds x" e "bonds y"

INPUT_FILE="$1"

if [ -z "$INPUT_FILE" ]; then
  echo "Uso: $0 arquivo.out"
  exit 1
fi

# Substitui linhas exatas "bonds x" e "bonds y" por versões com dois-pontos

sed -i  '' "/bonds x/s/.*/bonds x\:/g" "$INPUT_FILE"
sed -i  '' "/bonds y/s/.*/bonds y\:/g" "$INPUT_FILE"


sed -i  '' "/\<nk\>\:/s/.*/n\(q\)\:/g" "$INPUT_FILE"

