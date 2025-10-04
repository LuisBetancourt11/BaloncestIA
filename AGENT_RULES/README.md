# Reglas para agentes que modifiquen el código

Propósito
- Este documento establece reglas obligatorias para cualquier agente (humano o automatizado) que vaya a leer o modificar el código de este repositorio.

Reglas obligatorias
1. Todo lo que hagas, va a ir comentado para saber qué hacer
   - Cada función, clase y módulo nuevo o modificado debe incluir una docstring/título corto que explique su propósito.
   - Las partes complejas del código deben llevar comentarios inline que expliquen la intención y los supuestos.
   - Si añades scripts o utilidades, incluye un encabezado con: autor (o agente), fecha y breve descripción.

2. Todo lo que se modifique o realice se va a subir a GitHub en:
   https://github.com/LuisBetancourt11/BaloncestIA
   - Crea una rama por cada cambio significativo: `feature/desc`, `fix/desc`, `chore/desc`.
   - Siempre abre un Pull Request contra `main` con una descripción clara de los cambios.
   - Incluye en la descripción del PR: lista de archivos modificados, resumen de la lógica, pasos para probar y cualquier riesgo conocido.

Buenas prácticas adicionales (obligatorias cuando sea aplicable)
- Añade o actualiza tests unitarios que cubran el cambio (pytest está configurado en el proyecto).
- Ejecuta `pytest -q` localmente antes de abrir el PR y publica los resultados en la descripción del PR.
- Actualiza la documentación (README o archivos en `docs/`) si el comportamiento público cambia.
- No incluyas secretos en el repo; usa variables de entorno y añade entradas a `.gitignore` si creas archivos locales.

Comandos rápidos (PowerShell) para realizar cambios y subirlos
```powershell
# Crear rama
git checkout -b feature/mi-cambio

# Hacer cambios (editar archivos)
# ... editar ...

# Añadir y testear
git add .
pytest -q

# Commit con mensaje claro
git commit -m "feature: breve descripción del cambio"

# Push de la rama al remoto
git push -u origin feature/mi-cambio

# Luego crear PR desde GitHub hacia main
```

Plantilla breve de mensaje de commit
- Tipo: (feat|fix|chore|docs|test):
- Resumen corto (máx. 72 caracteres)
- Línea en blanco
- Descripción detallada (por qué se hizo el cambio, cómo probarlo)

Excepciones y aprobaciones
- Cualquier excepción a estas reglas debe ser aprobada explícitamente por el responsable del repo (owner) y documentada en el PR.

Contacto
- Repo owner / contacto: https://github.com/LuisBetancourt11

Mantén este archivo actualizado: cualquier agente que modifique estas reglas debe seguirlas también y abrir un PR con la justificación.
