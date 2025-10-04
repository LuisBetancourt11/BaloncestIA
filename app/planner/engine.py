from .rules import get_pattern, BLOCK_BASE, adjust_blocks_for_objectives, adjust_for_level, INTENSITY_TO_RPE
from .drills import load_drills, pick_drills_for_block
import math
from typing import List

DRILLS = load_drills()

DAY_ORDER = ['lun','mar','mie','jue','vie','sab','dom']


def round5(x):
    return int(5 * round(float(x)/5))


def allocate_minutes(total_min:int, blocks_pct:dict):
    # compute minutes per block and round to nearest 5, adjust to sum exactly
    alloc = {}
    for k,v in blocks_pct.items():
        alloc[k] = round5(total_min * v)
    # fix total
    s = sum(alloc.values())
    diff = total_min - s
    keys = list(alloc.keys())
    i = 0
    while diff != 0:
        alloc[keys[i % len(keys)]] += 5 if diff>0 else -5
        diff = total_min - sum(alloc.values())
        i += 1
    return alloc


def build_week_plan(disponibilidad:List[str], duracion_sesion_min:int, nivel:str, objetivos:List[str], equipamiento:List[str], historial_carga:List[dict]=None):
    dias_por_semana = len(disponibilidad)
    pattern = get_pattern(dias_por_semana)
    blocks_base = BLOCK_BASE.copy()
    blocks_adj = adjust_blocks_for_objectives(blocks_base, objetivos)
    blocks_adj = adjust_for_level(blocks_adj, nivel)

    weeks = []
    # for single microcycle (week 0)
    week = []
    for idx, dia in enumerate(disponibilidad):
        intensidad = pattern[idx % len(pattern)]
        # enforce no two Alta consecutivas
        if idx>0 and intensidad=='Alta' and pattern[(idx-1)%len(pattern)]=='Alta':
            intensidad='Media'
        # limit HIIT for principiantes: condicionamiento <=15%
        b_pct = blocks_adj.copy()
        if nivel=='principiante':
            b_pct['condicionamiento'] = min(b_pct.get('condicionamiento',0), 0.15)
        alloc = allocate_minutes(duracion_sesion_min, b_pct)
        # map categories to drill categories
        bloques = []
        for tipo, mins in alloc.items():
            if mins<=0:
                continue
            # map tipo names to drill categories
            cat = 'enfriamiento' if tipo=='movilidad' else tipo
            # choose intensity mapping
            intensidad_drill = 'baja' if intensidad=='Baja' else ('alta' if intensidad=='Alta' and tipo in ['condicionamiento'] else 'media')
            selected = pick_drills_for_block(DRILLS, categoria=cat if cat!='tiro' else 'tiro_movimiento', intensidad=intensidad_drill, equipamiento=equipamiento, minutes_needed=mins)
            if selected:
                desc = '; '.join([d.get('descripcion','') for d in selected])
            else:
                # use a neutral description that doesn't include equipment names like 'balon'
                desc = f'Bloque genérico ({mins} min) - sin drills disponibles según el equipamiento.'
            bloques.append({'tipo': tipo, 'min': mins, 'descripcion': desc})
        rpe = INTENSITY_TO_RPE.get(intensidad,5)
        carga = rpe * duracion_sesion_min
        session = {
            'dia': dia,
            'intensidad': intensidad,
            'duracion_min': duracion_sesion_min,
            'bloques': bloques,
            'indicadores': {'RPE': rpe, 'carga_sesion': carga}
        }
        week.append(session)
    weeks.append(week)

    # progression: if historial_carga provided, compute target weekly carga and adjust RPE if needed
    if historial_carga:
        last = sorted(historial_carga, key=lambda x: x.get('semana'))[-1]
        ultima = last.get('carga_total', None)
        if ultima:
            # target: no more than +15% from last week
            target = ultima * 1.15
            # Iteratively reduce RPEs to meet target (guardando mínimo RPE 3)
            current_week_carga = sum(s['indicadores']['carga_sesion'] for s in week)
            iterations = 0
            while current_week_carga > target and iterations < 5:
                reduction_factor = target / current_week_carga
                # apply reduction to each session's RPE
                for s in week:
                    old_rpe = s['indicadores']['RPE']
                    # scale and floor to avoid oscillation
                    new_rpe = max(3, int((old_rpe * reduction_factor) // 1))
                    if new_rpe < old_rpe:
                        s['indicadores']['RPE'] = new_rpe
                        s['indicadores']['carga_sesion'] = new_rpe * s['duracion_min']
                current_week_carga = sum(s['indicadores']['carga_sesion'] for s in week)
                iterations += 1
            # final check: if still slightly above target due to rounding, nudge down the largest session
            if current_week_carga > target:
                # find session with max carga and reduce its RPE by 1 where possible
                week_sorted = sorted(week, key=lambda s: s['indicadores']['carga_sesion'], reverse=True)
                for s in week_sorted:
                    if s['indicadores']['RPE'] > 3:
                        s['indicadores']['RPE'] -= 1
                        s['indicadores']['carga_sesion'] = s['indicadores']['RPE'] * s['duracion_min']
                        current_week_carga = sum(ss['indicadores']['carga_sesion'] for ss in week)
                        if current_week_carga <= target:
                            break
    return {'semanas':1, 'weeks': weeks}
