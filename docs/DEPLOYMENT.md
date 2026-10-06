# Deployment & Operations Guide

## 1. Environment Variables Configuration

Create a `.env` file from `.env.example`:

| Variable | Description | Default / Example | Required |
|---|---|---|---|
| `ENVIRONMENT` | Environment stage (`development` / `production`) | `production` | Yes |
| `SECRET_KEY` | Cryptographic secret key for signing JWT tokens | `<generate-random-64-char-hex>` | Yes |
| `DATABASE_URL` | Async SQLAlchemy database connection string | `postgresql+asyncpg://user:pass@host:5432/dbname` | Yes |
| `BACKEND_CORS_ORIGINS` | JSON list of allowed frontend origins | `["https://your-frontend.vercel.app"]` | Yes |
| `UPLOAD_DIR` | Absolute or relative path for sanitized uploads | `/app/uploads` | Yes |
| `MODEL_PATH` | Path to active ONNX model file | `ml/models/crop_disease_model.onnx` | Yes |
| `MODEL_INT8_PATH` | Path to active quantized INT8 ONNX model | `ml/models/crop_disease_model_int8.onnx` | No |
| `LABELS_PATH` | Path to JSON class label mapping | `ml/models/labels.json` | Yes |
| `DISEASES_KB_PATH` | Path to curated agronomic knowledge base YAML | `backend/app/knowledge_base/diseases.yaml` | Yes |
| `OPEN_METEO_BASE_URL` | Public endpoint for Open-Meteo weather API | `https://api.open-meteo.com/v1` | Yes |

---

## 2. Option A: Single VPS with Docker Compose (Recommended for Production)

### Requirements
- Ubuntu 22.04 LTS / Debian 12 VPS (2 vCPU, 2-4 GB RAM)
- Docker Engine & Docker Compose v2+ installed

### Steps:
1. **Clone repository onto VPS**:
   ```bash
   git clone https://github.com/your-username/crop-disease-ai.git
   cd crop-disease-ai
   ```
2. **Configure production `.env`**:
   ```bash
   cp .env.example .env
   # Edit SECRET_KEY and POSTGRES_PASSWORD
   ```
3. **Launch the complete stack**:
   ```bash
   docker compose up -d --build
   ```
4. **Verify services**:
   ```bash
   curl http://localhost:8000/api/v1/health
   # Expected: {"status":"healthy","database":"connected","model_loaded":true}
   ```
5. **Set up TLS Reverse Proxy (Caddy / Nginx Certbot)**:
   Example Caddyfile for automatic Let's Encrypt HTTPS:
   ```caddy
   yourdomain.com {
       reverse_proxy localhost:80
   }
   ```

---

## 3. Option B: Free-Tier Cloud Deployment (Serverless / Managed)

### Architecture
- **Database**: Free Managed PostgreSQL on [Neon.tech](https://neon.tech) or [Supabase](https://supabase.com).
- **Backend API**: Free/Hobby Container on [Render](https://render.com), [Railway](https://railway.app), or [Fly.io](https://fly.io).
- **Frontend UI**: Static SPA on [Vercel](https://vercel.com) or [Netlify](https://netlify.com).

### Step-by-Step Instructions:

#### Step 1: Provision Cloud Database (Neon / Supabase)
1. Sign up on [Neon.tech](https://neon.tech) and create a PostgreSQL database.
2. Copy the connection string: `postgres://user:password@ep-xyz.aws.neon.tech/neondb?sslmode=require`.
3. Prepend `postgresql+asyncpg://` for SQLAlchemy async driver.

#### Step 2: Deploy Backend to Render / Railway / Fly.io
1. Create a new **Web Service** pointing to your GitHub repository.
2. Set Environment to **Docker** (using `backend/Dockerfile`).
3. Set the following Environment Variables in the dashboard:
   - `DATABASE_URL`: Your async Neon connection string
   - `SECRET_KEY`: Generate a random 64-character secret
   - `BACKEND_CORS_ORIGINS`: `["https://crop-disease.vercel.app"]`
   - `ENVIRONMENT`: `production`
4. The service will build and start with the lightweight ONNX runtime engine (<350 MB RAM).

#### Step 3: Deploy Frontend to Vercel / Netlify
1. Connect your repository to [Vercel](https://vercel.com).
2. Set Root Directory to `frontend`.
3. Set Build Command to `npm run build` and Output Directory to `dist`.
4. Add Environment Variable:
   - `VITE_API_BASE_URL`: `https://your-backend.onrender.com/api/v1`
5. Deploy. The web app is now live with automatic worldwide CDN caching.
