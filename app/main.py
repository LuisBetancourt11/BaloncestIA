from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .schemas import PlanRequest, FeedbackIn
from . import models
from .db import engine, SessionLocal
from sqlalchemy.orm import Session
from .planner.engine import build_week_plan
from .planner.drills import load_drills
import csv
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import json
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount('/static', StaticFiles(directory=os.path.join(os.path.dirname(__file__),'static')), name='static')
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__),'templates'))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    drills = load_drills()
    return templates.TemplateResponse('index.html', {'request': request, 'drills': drills})

@app.post('/api/plan')
async def api_plan(plan_req: PlanRequest, db: Session = Depends(get_db)):
    # build plan
    plan = build_week_plan(plan_req.disponibilidad, plan_req.duracion_sesion_min, plan_req.nivel, plan_req.objetivos, plan_req.equipamiento, plan_req.historial_carga)
    # save basic plan
    p = models.Plan(
        fecha_inicio='hoje',
        semanas=plan_req.semanas,
        nivel=plan_req.nivel,
        dias_por_semana=len(plan_req.disponibilidad),
        duracion_sesion_min=plan_req.duracion_sesion_min,
        objetivos_json=json.dumps(plan_req.objetivos, ensure_ascii=False),
        equipamiento_json=json.dumps(plan_req.equipamiento, ensure_ascii=False)
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    # save sessions/blocks
    for week_idx, week in enumerate(plan['weeks']):
        for s in week:
            sess = models.Session(plan_id=p.id, week_idx=week_idx, day_name=s['dia'], intensidad=s['intensidad'], duracion_min=s['duracion_min'], rpe=s['indicadores']['RPE'], carga=s['indicadores']['carga_sesion'])
            db.add(sess)
            db.commit()
            db.refresh(sess)
            for b in s['bloques']:
                bl = models.Block(session_id=sess.id, tipo=b['tipo'], min=b['min'], descripcion=b['descripcion'])
                db.add(bl)
            db.commit()
    return JSONResponse({'plan_id': p.id, 'plan': plan})

@app.get('/api/templates')
def api_templates():
    drills = load_drills()
    return JSONResponse({'drills': drills})

@app.post('/api/feedback')
def api_feedback(fb: FeedbackIn, db: Session = Depends(get_db)):
    # store feedback
    f = models.Feedback(plan_id=fb.plan_id, week_idx=fb.week_idx, cumplimiento_pct=fb.cumplimiento_pct, rpe_promedio=fb.rpe_promedio, notas=fb.notas)
    db.add(f)
    db.commit()
    return JSONResponse({'status': 'ok'})

@app.get('/api/plan/{plan_id}')
def get_plan(plan_id:int, db: Session = Depends(get_db)):
    p = db.query(models.Plan).filter(models.Plan.id==plan_id).first()
    if not p:
        raise HTTPException(status_code=404, detail='Plan not found')
    sessions = []
    for s in p.sessions:
        blocks = [{'tipo': b.tipo, 'min': b.min, 'descripcion': b.descripcion} for b in s.blocks]
        sessions.append({'week_idx': s.week_idx, 'dia': s.day_name, 'intensidad': s.intensidad, 'duracion_min': s.duracion_min, 'rpe': s.rpe, 'carga': s.carga, 'bloques': blocks})
    return JSONResponse({'plan': {'id': p.id, 'semanas': p.semanas, 'nivel': p.nivel, 'sessions': sessions}})

@app.get('/export/csv')
def export_csv(plan_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Plan).filter(models.Plan.id==plan_id).first()
    if not p:
        raise HTTPException(status_code=404, detail='Plan not found')
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['plan_id', 'week_idx','dia','intensidad','duracion_min','rpe','carga','bloque_tipo','bloque_min','bloque_desc'])
    for s in p.sessions:
        for b in s.blocks:
            writer.writerow([p.id, s.week_idx, s.day_name, s.intensidad, s.duracion_min, s.rpe, s.carga, b.tipo, b.min, b.descripcion])
    output.seek(0)
    return StreamingResponse(io.BytesIO(output.getvalue().encode('utf-8')), media_type='text/csv', headers={'Content-Disposition': f'attachment; filename=plan_{plan_id}.csv'})

@app.get('/export/pdf')
def export_pdf(plan_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Plan).filter(models.Plan.id==plan_id).first()
    if not p:
        raise HTTPException(status_code=404, detail='Plan not found')
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elems = []
    elems.append(Paragraph(f"Plan {p.id} - Nivel: {p.nivel}", styles['Heading2']))
    for s in p.sessions:
        elems.append(Paragraph(f"Semana {s.week_idx+1} - {s.day_name} ({s.intensidad}) - {s.duracion_min} min - RPE {s.rpe}", styles['Normal']))
        for b in s.blocks:
            elems.append(Paragraph(f" - {b.tipo}: {b.min} min - {b.descripcion}", styles['Bullet']))
    doc.build(elems)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type='application/pdf', headers={'Content-Disposition': f'attachment; filename=plan_{plan_id}.pdf'})
