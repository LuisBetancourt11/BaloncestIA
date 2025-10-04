from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_templates():
    r = client.get('/api/templates')
    assert r.status_code==200
    assert 'drills' in r.json()

def test_post_plan_and_get():
    payload = {
        "nivel":"intermedio",
        "semanas":1,
        "disponibilidad":["lun","mar","jue"],
        "duracion_sesion_min":60,
        "objetivos":["mejorar tiro"],
        "equipamiento":["balon"]
    }
    r = client.post('/api/plan', json=payload)
    assert r.status_code==200
    data = r.json()
    assert 'plan_id' in data
    plan_id = data['plan_id']
    r2 = client.get(f'/api/plan/{plan_id}')
    assert r2.status_code==200
    assert 'plan' in r2.json()
