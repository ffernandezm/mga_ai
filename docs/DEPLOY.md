# Despliegue gratuito (académico)

Stack desplegado:

- **Frontend** (Vite + React) → **Vercel**
- **Backend** (FastAPI) → **Render** (Docker, plan Free)
- **Base de datos** (PostgreSQL) → **Neon** (Free tier permanente)
- **LLM** → **Groq API**

Resultado: dos URLs HTTPS públicas que cualquier usuario puede usar.
**Todo el stack es 100% gratis y NO requiere tarjeta de crédito.**

> Rama de despliegue: **`main_deployment`** (configurada en `render.yaml`
> y debe seleccionarse también en Vercel como "Production Branch").

> ⚠️ El plan Free de Render duerme el servicio tras ~15 min sin tráfico.
> La primera petición tras dormir tarda ~30–60 s. Para evitarlo, usa
> Koyeb o Fly.io en lugar de Render con la misma configuración Docker.

---

## 1. Subir el repo a GitHub

```bash
git checkout main_deployment
git add .
git commit -m "chore: preparar deploy"
git push origin main_deployment
```

Asegúrate de que `.env`, `venv_fastapi_new/` y `node_modules/` están ignorados.

---

## 2. Crear la base de datos en Neon

1. Entra a https://neon.tech y crea un proyecto (por ejemplo `mga`).
2. Copia el `DATABASE_URL` (formato `postgresql://user:pass@host/db?sslmode=require`).
3. Guárdala, la usarás en Render.

(Si ya tienes datos locales que quieras subir, exporta con
`pg_dump` y carga con `psql "$DATABASE_URL" < dump.sql`.)

---

## 3. Desplegar el backend en Render

1. Entra a https://render.com → **New +** → **Blueprint**.
2. Selecciona el repo. Detectará el archivo `render.yaml` de la raíz.
3. Render creará el servicio `mga-backend` usando el `Dockerfile` de `backend/`.
4. En **Environment** del servicio, configura las variables sensibles:
   - `DATABASE_URL` → la URL de Neon
   - `GROQ_API_KEY` → tu API key de Groq (https://console.groq.com)
   - `FRONTEND_URL` → la URL de Vercel (se sabrá tras el paso 4). Si aún no la tienes, déjala vacía por ahora.
5. Haz **Deploy**. El contenedor ejecuta `alembic upgrade head` y arranca uvicorn.
6. Verifica:
   - `https://<tu-backend>.onrender.com/health` → `{"status":"healthy", ...}`
   - `https://<tu-backend>.onrender.com/docs` → Swagger.

---

## 4. Desplegar el frontend en Vercel

1. Entra a https://vercel.com → **Add New… → Project**.
2. Importa el repo. En **Root Directory** elige `frontend`.
3. En **Settings → Git → Production Branch**, selecciona `main_deployment`.
4. Framework: **Vite** (autodetectado). El `vercel.json` ya configura rewrites SPA.
5. En **Environment Variables**, añade:
   - `VITE_API_URL` = `https://<tu-backend>.onrender.com`
6. **Deploy**.
7. Copia la URL (ej. `https://mga-ai.vercel.app`).

---

## 5. Cerrar el círculo (CORS)

1. Vuelve a Render → servicio `mga-backend` → Environment.
2. Edita `FRONTEND_URL` con la URL real de Vercel (sin barra final).
   - Puedes poner varias separadas por coma: `https://mga-ai.vercel.app,https://otra.com`.
3. Render redeploy automático. Listo.

---

## 6. Probar

- Abre la URL de Vercel.
- Inspecciona en DevTools → Network: las requests deben ir a tu URL de Render.
- Si ves errores CORS, revisa que `FRONTEND_URL` coincida exactamente con el origen del navegador.

---

## Variables de entorno (resumen)

### Backend (Render)
| Variable | Ejemplo |
|---|---|
| `ENVIRONMENT` | `production` |
| `DATABASE_URL` | `postgresql://…neon.tech/mga?sslmode=require` |
| `LLM_PROVIDER` | `groq` |
| `GROQ_API_KEY` | `gsk_…` |
| `GROQ_MODEL` | `llama-3.1-8b-instant` |
| `FRONTEND_URL` | `https://mga-ai.vercel.app` |

### Frontend (Vercel)
| Variable | Ejemplo |
|---|---|
| `VITE_API_URL` | `https://mga-backend.onrender.com` |

---

## Probar el build localmente (opcional)

```bash
# Backend
cd backend
docker build -t mga-backend .
docker run --rm -p 8000:8000 --env-file .env mga-backend

# Frontend
cd frontend
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm install
npm run build
npm run preview
```

---

## Alternativas si Render Free se queda corto

- **Fly.io** (no se duerme, 256 MB gratis): `fly launch` usando el mismo `Dockerfile`.
- **Koyeb** (1 servicio gratis, 512 MB, sin dormir).
- **Railway** (~$5 crédito/mes gratis).

Todas leen el mismo `Dockerfile`, solo cambia la plataforma.
