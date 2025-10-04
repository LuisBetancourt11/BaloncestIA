from typing import List

INTENSITY_PATTERNS = {
    3: ['Alta','Media','Baja'],
    4: ['Alta','Media','Alta','Baja'],
    5: ['Alta','Media','Alta','Media','Baja'],
    6: ['Alta','Media','Alta','Media','Baja','Baja']
}

BLOCK_BASE = {
    'calentamiento': 0.10,
    'manejo_balon': 0.25,
    'tiro': 0.30,
    'defensa': 0.15,
    'condicionamiento': 0.15,
    'movilidad': 0.05
}

def get_pattern(dias_por_semana:int):
    if dias_por_semana < 3:
        dias_por_semana = 3
    if dias_por_semana >6:
        dias_por_semana = 6
    pattern = INTENSITY_PATTERNS.get(dias_por_semana)
    # ensure last day is Baja
    if pattern and pattern[-1] != 'Baja':
        pattern[-1] = 'Baja'
    return pattern

def adjust_blocks_for_objectives(blocks_pct:dict, objetivos:List[str]):
    b = blocks_pct.copy()
    for o in objetivos:
        lo = o.lower()
        if 'tiro' in lo:
            b['tiro'] = min(0.6, b.get('tiro',0)+0.10)
            b['condicionamiento'] = max(0.05, b.get('condicionamiento',0)-0.05)
        if 'manejo' in lo or 'balon' in lo:
            b['manejo_balon'] = min(0.6, b.get('manejo_balon',0)+0.10)
            b['tiro'] = max(0.05, b.get('tiro',0)-0.05)
        if 'resistencia' in lo or 'aceler' in lo:
            b['condicionamiento'] = min(0.6, b.get('condicionamiento',0)+0.10)
            b['manejo_balon'] = max(0.05, b.get('manejo_balon',0)-0.05)
        if 'defensa' in lo:
            b['defensa'] = min(0.5, b.get('defensa',0)+0.10)
            b['tiro'] = max(0.05, b.get('tiro',0)-0.05)
    # normalize to sum 1.0
    s = sum(b.values())
    if s == 0:
        return blocks_pct
    for k in b:
        b[k] = b[k] / s
    return b

def adjust_for_level(blocks_pct:dict, nivel:str):
    b = blocks_pct.copy()
    if nivel == 'principiante':
        b['manejo_balon'] = min(0.6, b.get('manejo_balon',0)+0.05)
        b['tiro'] = max(0.1, b.get('tiro',0)-0.03)
        b['condicionamiento'] = max(0.05, b.get('condicionamiento',0)-0.02)
    if nivel == 'avanzado':
        b['condicionamiento'] = min(0.6, b.get('condicionamiento',0)+0.03)
        b['tiro'] = min(0.6, b.get('tiro',0)+0.03)
    # re-normalize
    s = sum(b.values())
    for k in b:
        b[k] = b[k] / s
    return b

INTENSITY_TO_RPE = {'Baja':3,'Media':5,'Alta':7}
