import re
from typing import Dict, List, Optional, Any

NUMBER_RE = r'[+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+\-]?\d+)?'

def _to_snake(name: str) -> str:
    s = name.strip().replace('/', ' per ')
    s = re.sub(r'[^0-9a-zA-Z]+', '_', s)
    s = re.sub(r'_+', '_', s)
    return s.strip('_').lower()

_PM_ANY = r'(?:\+\-|(?:\+\/\-)|±)'

_MAIN = re.compile(
    rf'^\s*(Average\s+.+?)\s*=\s*(?P<val>{NUMBER_RE})(?:\s*{_PM_ANY}\s*(?P<err>{NUMBER_RE})\s*)?$',
    flags=re.IGNORECASE
)

_TRAILING_PM = re.compile(rf'{_PM_ANY}\s*\Z')
_LONE_NUM = re.compile(rf'^\s*(?P<num>{NUMBER_RE})\b')

def parse_block(text: str) -> Dict[str, Any]:
    raw_lines = text.splitlines()

    # 1) Refluir linhas que terminam com "+-", "+/-" ou "±" (com ou sem espaços finais)
    lines: List[str] = []
    i, n = 0, len(raw_lines)
    while i < n:
        cur = raw_lines[i].rstrip(' \t\r\x0b\x0c\xa0')
        if _TRAILING_PM.search(cur):
            # achar próxima linha não vazia
            j = i + 1
            while j < n and raw_lines[j].strip() == '':
                j += 1
            if j < n:
                # cola a próxima linha (strip à esquerda p/ não criar dois espaços)
                cur = cur + ' ' + raw_lines[j].lstrip()
                i = j  # consumiu a linha do erro também
        lines.append(cur)
        i += 1

    # 2) Agora aplicar a regex normalmente
    items: List[Dict[str, Any]] = []
    for line in lines:
        m = _MAIN.match(line)
        if m:
            name = m.group(1).strip()
            val = float(m.group('val'))
            err: Optional[float] = None

            if m.group('err') is not None:
                err = float(m.group('err'))
            else:
                # fallback: se ainda sobrou caso de quebra não tratado
                # tenta ler um número após "+-" na própria linha refluída
                # (já deve estar colado, mas deixo por segurança)
                pass

            items.append({
                "name": name,
                "key": _to_snake(name),
                "value": val,
                "error": err
            })

    return {"block": "averages", "count": len(items), "items": items}