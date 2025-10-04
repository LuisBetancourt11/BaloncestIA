"""Utilities to load and pick drills from the YAML library.

The drills library is a YAML mapping in `data/drills.yml`. We expose helpers
to load the library, filter by metadata and pick a set of drills to fill a
time budget for a block.

Design notes:
- `load_drills` returns a list of dicts with an `id` field for traceability.
- `filter_drills` performs exact matching by category/intensity and checks
  equipment subset requirements.
- `pick_drills_for_block` tries to fill the requested minutes by adding
  suggested durations; randomness is only used to vary selection order.
"""

import yaml
from pathlib import Path
import random

DRILLS_PATH = Path(__file__).resolve().parents[2] / 'data' / 'drills.yml'


def load_drills(path=None):
    """Load drills from YAML and return as a list of dicts.

    If no path is provided the default `data/drills.yml` next to the repo
    root is used. Returns an empty list if the file cannot be found.
    """
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

    drills = []
    for k, v in data.items():
        item = v.copy()
        item['id'] = k
        drills.append(item)
    return drills


def filter_drills(drills, categoria=None, intensidad=None, equipamiento=None):
    """Return drills matching the given metadata filters.

    - `equipamiento` is treated as a superset: a drill requiring certain items
      will be included only if all required items are present in `equipamiento`.
    """
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
    """Pick drills to approximately fill `minutes_needed`.

    The function attempts to select drills from the filtered pool until the
    accumulated suggested minutes meet or exceed the minutes_needed. It
    returns a list of drill dicts (possibly empty).
    """
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
