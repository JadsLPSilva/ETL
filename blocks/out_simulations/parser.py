import re
import pandas as pd

# int/float incluindo notação científica
NUM = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?'

header_patterns = {
    "tausk":               re.compile(r'^\s*tausk=\s*(\d+)\s*$', re.M),
    "phonskip":            re.compile(r'^\s*phonskip=\s*(\d+)\s*$', re.M),
    "numtry_gsize":        re.compile(r'^\s*numtry,gsize\s*\n\s*(\d+)\s+(' + NUM + r')', re.M),
    "lambda0":             re.compile(r'^\s*lambda0 is\s*(' + NUM + r')', re.M),
    "istart":              re.compile(r'^\s*istart is\s*(\d+)', re.M),
    "init_ph_scale":       re.compile(r'^\s*initial phonon scale is\s*(' + NUM + r')', re.M),
    "init_bond_x":         re.compile(r'^\s*initial bond field X\s*(' + NUM + r')', re.M),
    "init_bond_y":         re.compile(r'^\s*initial bond field Y\s*(' + NUM + r')', re.M),
    "mu":                  re.compile(r'^\s*Using mu =\s*(' + NUM + r')', re.M),
    "accept_hol_warm":     re.compile(r'accept holstein ratio is\s*(' + NUM + r')', re.M),
    "accept2_ssh_warm":    re.compile(r'accept2 SSH ratio is\s*(' + NUM + r')', re.M),
    "accept2_hol_warm":    re.compile(r'accept2 Holstein ratio is\s*(' + NUM + r')', re.M),
    "gamma":               re.compile(r'^\s*gamma is\s*(' + NUM + r')', re.M),
    "redo_ratio_warmup":   re.compile(r'^\s*redo ratio is\s*(' + NUM + r')', re.M),
    "redo_ratio_end":      re.compile(r'^\s*At end, redo ratio is\s*(' + NUM + r')', re.M),
    "accept2_ssh_end":     re.compile(r'^\s*Accept2 SSH=\s*(' + NUM + r')', re.M),
    "accept2_hol_end":     re.compile(r'^\s*Accept2 Hol\.\=\s*(' + NUM + r')', re.M),
}

sweep_pat = re.compile(
    r'Finished measurement sweep\s*(\d+)\s*'
    r'asgn,\s*asgnp:\s*(' + NUM + r')\s*(' + NUM + r')\s*;accept holstein ,redo ratios:\s*(' + NUM + r')\s*(' + NUM + r')\s*'
    r'Total_meas=\s*(\d+)\s*'
    r'nwrap,\s*torth\s*=\s*(\d+)\s*(\d+)',
    re.M
)

def parse_block(text: str):
    """
    Recebe todo o texto de um .out/.log e devolve dois DataFrames:
    - df_header: 1 linha com metadados do run
    - df_sweeps: N linhas (uma por sweep) com métricas
    """
    def first_float(pat):
        m = pat.search(text)
        return float(m.group(1)) if m else None

    def first_int(pat):
        m = pat.search(text)
        return int(m.group(1)) if m else None

    header = {}
    header["tausk"] = first_int(header_patterns["tausk"])
    header["phonskip"] = first_int(header_patterns["phonskip"])

    m = header_patterns["numtry_gsize"].search(text)
    if m:
        header["numtry"] = int(m.group(1))
        header["gsize"] = float(m.group(2))
    else:
        header["numtry"] = None
        header["gsize"] = None

    header["lambda0"] = first_float(header_patterns["lambda0"])
    header["istart"] = first_int(header_patterns["istart"])

    # Duas ocorrências de "initial phonon scale is ..."
    init_scales = header_patterns["init_ph_scale"].finditer(text)
    scales = [float(mm.group(1)) for mm in init_scales]
    header["initial_phonon_scale_1"] = scales[0] if len(scales) > 0 else None
    header["initial_phonon_scale_2"] = scales[1] if len(scales) > 1 else None

    header["initial_bond_field_x"] = first_float(header_patterns["init_bond_x"])
    header["initial_bond_field_y"] = first_float(header_patterns["init_bond_y"])
    header["mu"] = first_float(header_patterns["mu"])
    header["accept_holstein_warmup"] = first_float(header_patterns["accept_hol_warm"])
    header["accept2_ssh_warmup"] = first_float(header_patterns["accept2_ssh_warm"])
    header["accept2_holstein_warmup"] = first_float(header_patterns["accept2_hol_warm"])
    header["gamma"] = first_float(header_patterns["gamma"])
    header["redo_ratio_warmup"] = first_float(header_patterns["redo_ratio_warmup"])
    header["redo_ratio_end"] = first_float(header_patterns["redo_ratio_end"])
    header["accept2_ssh_end"] = first_float(header_patterns["accept2_ssh_end"])
    header["accept2_hol_end"] = first_float(header_patterns["accept2_hol_end"])

    # Sweeps
    sweeps = []
    for m in sweep_pat.finditer(text):
        sweep = {
            "sweep": int(m.group(1)),
            "asgn": float(m.group(2)),
            "asgnp": float(m.group(3)),
            "accept_holstein": float(m.group(4)),
            "redo_ratio_sweep": float(m.group(5)),
            "total_meas": int(m.group(6)),
            "nwrap": int(m.group(7)),
            "torth": int(m.group(8)),
        }
        sweeps.append(sweep)

    df_header = pd.DataFrame([header])
    df_sweeps = pd.DataFrame(sweeps).sort_values("sweep").reset_index(drop=True)
    return df_header, df_sweeps