"""Planner engine: build_week_plan and helpers.

This module contains the logic that converts user inputs (availability,
session length, level, objectives and available equipment) into a
microcycle (week) composed of sessions and blocks.

Design notes / rules for contributors:
- Keep the builder deterministic where possible (randomness only in drill
  selection ordering; seed in tests if needed).
- Document any heuristics and magic numbers (e.g. RPE floor, progression limit).
"""

from .rules import get_pattern, BLOCK_BASE, adjust_blocks_for_objectives, adjust_for_level, INTENSITY_TO_RPE
from .drills import load_drills, pick_drills_for_block
from typing import List

# Load drills once per process to avoid repeated file IO
DRILLS = load_drills()

# Standard ordering used in some heuristics
DAY_ORDER = ['lun', 'mar', 'mie', 'jue', 'vie', 'sab', 'dom']


def round5(x):
    """Round an integer to the nearest multiple of 5.

    Used to keep block durations aligned to 5-minute increments.
    """
    return int(5 * round(float(x) / 5))


def allocate_minutes(total_min: int, blocks_pct: dict):
    """Allocate minutes to each block category based on percentages.

    - Rounds each allocation to nearest 5 minutes
    - Adjusts the allocations so the sum equals total_min by nudging buckets
      by ±5 minutes until the total matches.
    """
    alloc = {}
    for k, v in blocks_pct.items():
        alloc[k] = round5(total_min * v)
    # fix total to match exactly
    s = sum(alloc.values())
    diff = total_min - s
    keys = list(alloc.keys())
    i = 0
    while diff != 0:
        alloc[keys[i % len(keys)]] += 5 if diff > 0 else -5
        diff = total_min - sum(alloc.values())
        i += 1
    return alloc


def build_week_plan(disponibilidad: List[str], duracion_sesion_min: int, nivel: str, objetivos: List[str], equipamiento: List[str], historial_carga: List[dict] = None):
    """Build a single-week microcycle based on inputs.

    Returns a dict with 'semanas' and 'weeks' where each week is a list of
    session dicts. Each session contains blocks with type, minutes and
    description.
    """
    dias_por_semana = len(disponibilidad)
    pattern = get_pattern(dias_por_semana)

    # Start with the baseline block percentages and adjust for objectives/level
    blocks_base = BLOCK_BASE.copy()
    blocks_adj = adjust_blocks_for_objectives(blocks_base, objetivos)
    blocks_adj = adjust_for_level(blocks_adj, nivel)

    weeks = []

    # Build a single microcycle (week 0)
    week = []
    for idx, dia in enumerate(disponibilidad):
        intensidad = pattern[idx % len(pattern)]

        # Heuristic: avoid two consecutive 'Alta' intensity days
        if idx > 0 and intensidad == 'Alta' and pattern[(idx - 1) % len(pattern)] == 'Alta':
            intensidad = 'Media'

        # For beginners, cap intense conditioning blocks
        b_pct = blocks_adj.copy()
        if nivel == 'principiante':
            b_pct['condicionamiento'] = min(b_pct.get('condicionamiento', 0), 0.15)

        alloc = allocate_minutes(duracion_sesion_min, b_pct)

        bloques = []
        for tipo, mins in alloc.items():
            if mins <= 0:
                continue

            # Map internal block names to drill categories where needed
            cat = 'enfriamiento' if tipo == 'movilidad' else tipo

            # Map session intensity to drill intensity labels
            intensidad_drill = (
                'baja' if intensidad == 'Baja' else ('alta' if intensidad == 'Alta' and tipo in ['condicionamiento'] else 'media')
            )

            selected = pick_drills_for_block(
                DRILLS,
                categoria=(cat if cat != 'tiro' else 'tiro_movimiento'),
                intensidad=intensidad_drill,
                equipamiento=equipamiento,
                minutes_needed=mins,
            )

            if selected:
                desc = '; '.join([d.get('descripcion', '') for d in selected])
            else:
                # Neutral fallback text avoids mentioning equipment
                desc = f'Bloque genérico ({mins} min) - sin drills disponibles según el equipamiento.'

            bloques.append({'tipo': tipo, 'min': mins, 'descripcion': desc})

        rpe = INTENSITY_TO_RPE.get(intensidad, 5)
        carga = rpe * duracion_sesion_min

        session = {
            'dia': dia,
            'intensidad': intensidad,
            'duracion_min': duracion_sesion_min,
            'bloques': bloques,
            'indicadores': {'RPE': rpe, 'carga_sesion': carga},
        }
        week.append(session)

    weeks.append(week)

    # Progression logic: if there is historical load data, ensure the new
    # week's total load does not exceed +15% of the last recorded week.
    if historial_carga:
        last = sorted(historial_carga, key=lambda x: x.get('semana'))[-1]
        ultima = last.get('carga_total', None)
        if ultima:
            target = ultima * 1.15
            current_week_carga = sum(s['indicadores']['carga_sesion'] for s in week)
            iterations = 0
            while current_week_carga > target and iterations < 5:
                reduction_factor = target / current_week_carga
                for s in week:
                    old_rpe = s['indicadores']['RPE']
                    new_rpe = max(3, int((old_rpe * reduction_factor) // 1))
                    if new_rpe < old_rpe:
                        s['indicadores']['RPE'] = new_rpe
                        s['indicadores']['carga_sesion'] = new_rpe * s['duracion_min']
                current_week_carga = sum(s['indicadores']['carga_sesion'] for s in week)
                iterations += 1

            # If rounding keeps us slightly above target, reduce RPE of the
            # highest-load session by 1 until we meet the target.
            if current_week_carga > target:
                week_sorted = sorted(week, key=lambda s: s['indicadores']['carga_sesion'], reverse=True)
                for s in week_sorted:
                    if s['indicadores']['RPE'] > 3:
                        s['indicadores']['RPE'] -= 1
                        s['indicadores']['carga_sesion'] = s['indicadores']['RPE'] * s['duracion_min']
                        current_week_carga = sum(ss['indicadores']['carga_sesion'] for ss in week)
                        if current_week_carga <= target:
                            break

    return {'semanas': 1, 'weeks': weeks}
