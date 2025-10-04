import yaml
from pathlib import Path
import random

DRILLS_PATH = Path(__file__).resolve().parents[2] / 'data' / 'drills.yml'

def load_drills(path=None):
    p = Path(path) if path else DRILLS_PATH
    if not p.exists():
        # fallback: try relative path one level up
        alt = Path(__file__).resolve().parents[1] / 'data' / 'drills.yml'
        if alt.exists():
            p = alt
        else:
            return []
    with open(p, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    # return as list of dicts with id
    drills = []
    for k, v in data.items():
        item = v.copy()
        item['id'] = k
        drills.append(item)
    return drills

def filter_drills(drills, categoria=None, intensidad=None, equipamiento=None):
    out = []
    for d in drills:
        if categoria and d.get('categoria') != categoria:
            continue
        if intensidad and d.get('intensidad') != intensidad:
            continue
        req = set(d.get('equipo_requerido', []))
        if equipamiento is not None:
            if not req.issubset(set(equipamiento)):
                continue
        out.append(d)
    return out

def pick_drills_for_block(drills, categoria, intensidad, equipamiento, minutes_needed):
    pool = filter_drills(drills, categoria=categoria, intensidad=intensidad, equipamiento=equipamiento)
    random.shuffle(pool)
    selected = []
    total = 0
    for d in pool:
        if total >= minutes_needed:
            break
        selected.append(d)
        total += d.get('min_sugeridos', 5)
    return selected
