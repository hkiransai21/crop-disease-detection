# 🌿 AgriShield: AI Crop Disease Detection & Outbreak Risk Prediction System

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-CPU-005CED.svg)](https://onnxruntime.ai/)
[![Coverage](https://img.shields.io/badge/Backend_Coverage-83%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AgriShield is an end-to-end, **100% software-based** agricultural decision-support system designed to empower farmers and agricultural extension workers. Without requiring specialized hardware, IoT sensors, or physical probes, AgriShield combines:
1. **Computer Vision Disease Classification**: Real-time foliar lesion identification across 38 crop disease classes using an optimized `EfficientNet-B0` model.
2. **Environmental Outbreak Risk Engine**: Rule-based epidemiological modeling that fetches real-time weather from public meteorological APIs (Open-Meteo) to compute a transparent 0–100 Outbreak Spread Index.
3. **University Extension Knowledge Base**: Curated, multi-tiered recommendations (cultural sanitation, organic remedies, and chemical interventions with exact dosages and university safety notes).
4. **Accurate Regional Multilingual Support**: Comprehensive translations across 9 languages (English, हिन्दी, తెలుగు, தமிழ், ಕನ್ನಡ, മലയാളം, मराठी, বাংলা, Español) covering all UI text, disease names, and extension protocols.
5. **High-Quality Neural Audio Narration**: Natural-sounding regional voice narration with correct local disease names and agronomic terminology, powered by pluggable neural TTS (Microsoft Neural Edge / Cloud), offline PWA caching, and fallback speech synthesis.


---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Farmer Device [Farmer Client - Mobile / Desktop PWA]
        UI[React 18 + Tailwind CSS UI]
        Cam[Camera Capture / Downscaler]
        Storage[IndexedDB / Local Cache]
    end

    subgraph Backend Services [FastAPI Application]
        Router[API Gateway & Router]
        AuthService[JWT Authentication & Bcrypt]
        ImgProcessor[EXIF Stripper & Image Validator]
        
        subgraph Inference Engine [ML Subsystem]
            ONNX[ONNX Runtime CPU Session]
            Calibrator[Temperature Scaler T=0.4130]
            EntropyCheck[Shannon Entropy Rejection]
        end

        subgraph Advisory Engine [Agronomic Subsystem]
            WeatherSvc[Open-Meteo Live Weather & Geocoding]
            RiskEngine[Heuristic Outbreak Spread Engine]
            ExtensionKB[University Extension Knowledge Base]
        end

        DB[(SQLite / PostgreSQL via SQLAlchemy Async)]
    end

    subgraph Public APIs [External Public Services]
        OpenMeteo[Open-Meteo Weather API]
        GeoAPI[Open-Meteo Geocoding API]
    end

    Cam --> UI
    UI -->|1. Multipart Image Upload + Lat/Lng| Router
    Router --> AuthService
    Router --> ImgProcessor
    ImgProcessor --> ONNX
    ONNX --> Calibrator
    Calibrator --> EntropyCheck
    
    Router --> WeatherSvc
    WeatherSvc -->|HTTP REST| OpenMeteo
    WeatherSvc -->|HTTP REST| GeoAPI
    
    EntropyCheck --> RiskEngine
    WeatherSvc --> RiskEngine
    ExtensionKB --> RiskEngine
    
    RiskEngine --> DB
    RiskEngine -->|Consolidated JSON Response| UI
```

---

## 📊 Measured ML Benchmarks & Real Performance

All metrics below are derived directly from verified benchmark runs saved in [`ml/reports/`](file:///Users/sachinrk/Desktop/kiran/ml/reports/):

### 1. Classification Performance (PlantVillage Held-Out Test Set, $N = 8,237$)
- **Top-1 Test Accuracy**: `94.22%`
- **Top-3 Test Accuracy**: `99.08%`
- **Macro-Averaged F1**: `0.9232` (92.32%)
- **Weighted-Averaged F1**: `0.9420` (94.20%)
- **Macro Precision**: `0.9279` | **Macro Recall**: `0.9217`

### 2. Generalization Gap (Lab vs Real-World Field Benchmark, $N = 2,572$)
- **PlantVillage (Lab Conditions)**: `94.22% Accuracy`
- **PlantDoc (Real Field Conditions)**: `21.30% Accuracy`
- **Generalization Gap**: `72.92% drop` due to complex background foliage, variable lighting, and partial occlusions in field conditions.
- *Mitigation*: Uncalibrated softmax probabilities exhibited high overconfidence ($ECE = 25.71\%$). Post-hoc temperature calibration reduced $ECE$ to **$0.50\%$**, and high-entropy predictions ($H > 2.20$) trigger automatic uncertainty flags.

### 3. CPU Edge Runtime Latency (Apple Silicon M-Series Single-Thread CPU)
- **Model Architecture**: `EfficientNet-B0` (FP32 ONNX)
- **Model Graph Size**: `15.45 MB`
- **Median Inference Latency**: `7.64 ms` (**130.9 FPS**)
- **95th Percentile Latency**: `8.74 ms`
- **99th Percentile Latency**: `10.04 ms`
- **PyTorch/ONNX Max Parity Difference**: `$1.73 \times 10^{-6}$`

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.10+ (Recommended: 3.12)
- Node.js 18+ (Recommended: 20+)
- Git

### 1. Clone & Setup Environment
```bash
git clone https://github.com/your-org/crop-disease-risk-system.git
cd crop-disease-risk-system

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python backend and ML dependencies
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt
```

### 2. Start Backend API Server
```bash
# From workspace root
source .venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The FastAPI documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Start Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🐳 Docker Deployment

To launch the complete containerized stack (Backend, Frontend, PostgreSQL, Prometheus) with a single command:

```bash
docker-compose up --build -d
```

- **Frontend App**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Prometheus Metrics**: [http://localhost:9090](http://localhost:9090)

---

## 🧪 Testing & Validation

### Run Backend Unit & Integration Tests (83% Coverage)
```bash
source .venv/bin/activate
PYTHONPATH=. pytest backend/tests ml/tests --cov=backend/app --cov-report=term-missing
```

### Run Frontend Component Tests
```bash
cd frontend
npm run test
```

---

## 🌐 Multilingual Regional Support & Kisan Audio Assistant

AgriShield includes end-to-end regional language localization and neural speech narration across **9 languages**:

- **Languages Supported:** English (`en`), Hindi (`hi`), Telugu (`te`), Tamil (`ta`), Kannada (`kn`), Malayalam (`ml`), Marathi (`mr`), Bengali (`bn`), and Spanish (`es`).
- **Zero-Cost Neural Audio Narration:** Powered by `edge-tts` Microsoft Neural voices mapped to authentic regional speakers (e.g. `hi-IN-SwaraNeural`, `te-IN-ShrutiNeural`, `ta-IN-PallaviNeural`).
- **Offline-First Audio Caching:** Pre-generated audio is stored with content-addressed hashes in `backend/app/static/audio_cache/` and cached for offline use in the PWA.
- **Phonetic Pronunciation Lexicons:** Dedicated glossaries (`i18n/glossary/{lang}.json`) ensure plant pathology terms and dosages are pronounced correctly without robotic artifacts.
- **Safety & Parity Gates:** Strict automated parity verification (`backend/tests/test_i18n.py`) checks that all active ingredients, chemical dosages (e.g., 2.5g/L, 5ml/L, 15L pumps), and emergency helpline numbers (1800-180-1551) match exactly.

### Pre-generate Audio Narration Cache
```bash
# Pre-generate narration audio for all languages and sections
python scripts/generate_audio.py --lang all

# Pre-generate for a single language
python scripts/generate_audio.py --lang te
```

### Agronomist Translation Review Workflow
To export translations to CSV for university agronomists and re-import verified records:
```bash
# Export translations to CSV
python scripts/export_translations_csv.py --lang all

# Re-import reviewed CSV back into versioned JSON
python scripts/import_translations_csv.py docs/reviews/translation_review_te.csv
```
Detailed instructions are documented in [docs/I18N.md](docs/I18N.md) and [docs/TRANSLATION_REVIEW.md](docs/TRANSLATION_REVIEW.md).


### Run End-to-End Smoke Test Journey
```bash
source .venv/bin/activate
python scripts/e2e_smoke_test.py
```

---

## 📡 API Overview

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new farmer account | No |
| `POST` | `/api/v1/auth/login` | Login and obtain JWT tokens | No |
| `POST` | `/api/v1/analyze` | Upload crop leaf image + coordinates for diagnosis & risk | Optional |
| `GET` | `/api/v1/history` | Retrieve user diagnosis history with pagination & filters | Yes |
| `POST` | `/api/v1/feedback` | Submit validation/correction feedback with retraining consent | Optional |
| `GET` | `/api/v1/diseases` | List all 38 diseases and treatment knowledge base | No |
| `GET` | `/api/v1/weather/current` | Fetch live Open-Meteo weather and geocoding | No |
| `GET` | `/health` | Application health and model readiness probe | No |
| `GET` | `/metrics` | Prometheus metrics endpoint | No |

---

## ⚠️ Limitations & Ethical Disclaimer

> **ADVISORY DISCLAIMER**: AgriShield is an educational and advisory decision-support tool. It is **not** a certified agronomist or regulatory body. Fungal, bacterial, and viral crop symptoms can overlap with nutritional deficiencies (e.g., nitrogen/iron chlorosis) and environmental scorch.
> 
> - **Always cross-reference with local agricultural extension offices** before purchasing or applying regulated chemical treatments.
> - **Always read and follow the pesticide label** in accordance with local, state, and federal agricultural regulations.
> - **Retraining Privacy**: User photos are only utilized for continuous model improvement if the user explicitly checks `consent_for_retraining = true`.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
