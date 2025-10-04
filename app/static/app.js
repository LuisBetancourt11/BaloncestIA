async function postPlan(payload){
  const res = await fetch('/api/plan', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  return res.json();
}

function createSessionCard(s){
  const card = document.createElement('div'); card.className='session-card';
  const title = document.createElement('h4'); title.innerText = `${s.dia} — ${s.intensidad}`;
  const duration = document.createElement('div'); duration.className='meta'; duration.innerText = `${s.duracion_min} min`;
  card.appendChild(title); card.appendChild(duration);
  const blocks = document.createElement('div');
  s.bloques.forEach(b=>{
    const be = document.createElement('div'); be.className='block'; be.innerText = `${b.tipo}: ${b.min} min`;
    blocks.appendChild(be);
  });
  card.appendChild(blocks);
  const ind = document.createElement('div'); ind.className='indicators';
  const rpe = document.createElement('div'); rpe.className='indicator'; rpe.innerHTML = `<div class='pill'>RPE ${s.indicadores.RPE}</div>`;
  const carga = document.createElement('div'); carga.className='indicator'; carga.innerHTML = `<div class='pill'>Carga ${s.indicadores.carga_sesion}</div>`;
  ind.appendChild(rpe); ind.appendChild(carga);
  card.appendChild(ind);
  return card;
}

document.addEventListener('DOMContentLoaded', ()=>{
  const form = document.getElementById('planForm');
  const grid = document.getElementById('sessionsGrid');
  let lastPlanId = null;
  form.addEventListener('submit', async e=>{
    e.preventDefault();
    const data = new FormData(form);
    const payload = {
      nivel: data.get('nivel'),
      semanas: parseInt(data.get('semanas')),
      disponibilidad: data.get('disponibilidad').split(',').map(s=>s.trim()),
      duracion_sesion_min: parseInt(data.get('duracion_sesion_min')),
      objetivos: data.get('objetivos').split(',').map(s=>s.trim()).filter(Boolean),
      equipamiento: data.get('equipamiento').split(',').map(s=>s.trim()).filter(Boolean)
    };
    const json = await postPlan(payload);
    lastPlanId = json.plan_id;
    grid.innerHTML = '';
    if(json.plan && json.plan.weeks){
      json.plan.weeks[0].forEach(s=> grid.appendChild(createSessionCard(s)));
    }
    // expose lastPlanId on export buttons
    document.getElementById('exportCsv').onclick = ()=>{ if(!lastPlanId) return alert('Genera un plan primero'); window.open(`/export/csv?plan_id=${lastPlanId}`,'_blank') };
    document.getElementById('exportPdf').onclick = ()=>{ if(!lastPlanId) return alert('Genera un plan primero'); window.open(`/export/pdf?plan_id=${lastPlanId}`,'_blank') };
  });
});
