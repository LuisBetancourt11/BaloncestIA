<<<<<<< HEAD
# BaloncestIA
Un sistema de IA que ayuda a la optimización de entrenamientos para jugadores amateur
=======
Planificador de entrenamientos de baloncesto

Instrucciones rápidas:

Construir imagen Docker:

```powershell
docker build -t plan-basket .
```

Ejecutar contenedor:

```powershell
docker run -p 8000:8000 plan-basket
```

o con docker-compose:

```powershell
docker compose up --build
```
````markdown
# BaloncestIA
Un sistema de IA que ayuda a la optimización de entrenamientos para jugadores amateur

Planificador de entrenamientos de baloncesto

Instrucciones rápidas:

Construir imagen Docker:

```powershell
docker build -t plan-basket .
```

Ejecutar contenedor:

```powershell
docker run -p 8000:8000 plan-basket
```

o con docker-compose:

```powershell
docker compose up --build
```

Probar con pytest:

```powershell
pytest -q
```

Ejemplo de petición:

```bash
curl -X POST http://localhost:8000/api/plan -H "Content-Type: application/json" -d '{
 "nivel":"intermedio",
 "semanas":4,
 "disponibilidad":["lun","mar","jue","sab"],
 "duracion_sesion_min":90,
 "objetivos":["mejorar tiro","resistencia"],
 "equipamiento":["balon","conos","bandas"]
}'
```

Despliegue con Firebase Hosting (proxy a Cloud Run)
-------------------------------------------------

Este repositorio puede usar Firebase Hosting como punto de entrada (dominio + SSL) y reenviar todas las peticiones a un servicio Cloud Run que ejecuta la imagen Docker.

Pasos resumidos:

1. Instalar y autenticarse:

```powershell
gcloud auth login
gcloud config set project baloncestoia-e0724
firebase login
```

2. Construir y desplegar la imagen en Cloud Run (desde la raíz del repo):

```powershell
gcloud builds submit --tag gcr.io/baloncestoia-e0724/plan-basket:latest
gcloud run deploy plan-basket --image gcr.io/baloncestoia-e0724/plan-basket:latest --platform managed --region us-central1
```

3. Configurar Firebase Hosting para reenviar al servicio Cloud Run:

- Edita `.firebaserc` y `firebase.json` en este repo, reemplaza `YOUR_FIREBASE_PROJECT_ID` y `plan-basket` si usas otro nombre.
- Inicializa hosting si no lo hiciste:

```powershell
firebase init hosting
```

4. Desplegar Hosting:

```powershell
firebase deploy --only hosting
```

Firebase te guiará para verificar el dominio y crear los registros DNS; una vez verificado, Firebase gestionará el certificado SSL.

Notas sobre base de datos en producción:
- SQLite no es recomendado en producción para Cloud Run (contenedores efímeros). Migra a Cloud SQL (Postgres) y configura `DATABASE_URL` en Cloud Run.
- Puedes exportar datos de `app.db` y reimportarlos a Postgres, o crear un script de migración con SQLAlchemy.

Seguridad y entorno:
- No expongas credenciales en el repo. Usa variables de entorno en Cloud Run para `DATABASE_URL` y `SECRET_KEY`.
- Habilita backups en Cloud SQL y configura IAM para acceso restringido.

Si quieres, puedo:
- A) Preparar el repo con `psycopg2-binary` y un script de migración SQLite→Postgres.
- B) Guiarte paso a paso mientras ejecutas los comandos `gcloud` y `firebase` en tu máquina.
- C) Generar los comandos exactos para mapear tu dominio y actualizar DNS.

Subir este proyecto a GitHub
--------------------------------
Si quieres subir este proyecto a GitHub desde tu máquina, hay un script que intenta automatizarlo si tienes la GitHub CLI (`gh`) instalada.

Usar el script (PowerShell, en la raíz del repo):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\create_github_repo_and_push.ps1 -repoName "BaloncestIA" -visibility "public"
```

Si no tienes `gh`, sigue estos pasos manuales:
```bash
# desde la raíz del proyecto
git init   # si no está inicializado
git add .
git commit -m "Initial commit"
# crea un repo en GitHub vía web: https://github.com/new
git remote add origin https://github.com/LuisBetancourt11/BaloncestIA.git
git branch -M main
git push -u origin main
```

Una vez subido a GitHub, vuelve a Cloud Shell y ejecuta los pasos de despliegue (clonar, build, deploy) tal como está documentado más arriba.

````
