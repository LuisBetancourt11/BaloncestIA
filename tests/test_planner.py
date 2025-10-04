from app.planner.engine import build_week_plan

def test_sumatoria_minutos_por_sesion():
    plan = build_week_plan(['lun','mar','jue'], 90, 'intermedio', ['mejorar tiro'], ['balon'])
    week = plan['weeks'][0]
    for s in week:
        total = sum(b['min'] for b in s['bloques'])
        assert total == s['duracion_min']

def test_no_dos_altas_seguidas():
    plan = build_week_plan(['lun','mar','mie'], 60, 'intermedio', [], ['balon'])
    intensidades = [s['intensidad'] for s in plan['weeks'][0]]
    for i in range(1,len(intensidades)):
        assert not (intensidades[i]=='Alta' and intensidades[i-1]=='Alta')

def test_al_menos_un_baja_por_semana():
    plan = build_week_plan(['lun','mar','mie','jue'], 60, 'intermedio', [], ['balon'])
    intensidades = [s['intensidad'] for s in plan['weeks'][0]]
    assert 'Baja' in intensidades

def test_seleccion_drills_respeta_equipamiento():
    plan = build_week_plan(['lun'], 60, 'intermedio', [], [])
    # drills requiring balon should not be selected if no balon
    week = plan['weeks'][0]
    for s in week:
        for b in s['bloques']:
            desc = b['descripcion']
            assert 'balon' not in desc.lower()

def test_progresion_carga_no_supera_15_por_ciento():
    hist = [{'semana':1,'carga_total':1000}]
    plan = build_week_plan(['lun','mar','jue'], 90, 'intermedio', [], ['balon'], historial_carga=hist)
    week = plan['weeks'][0]
    current = sum(s['indicadores']['carga_sesion'] for s in week)
    assert current <= 1000*1.15
