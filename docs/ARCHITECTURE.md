# System Architecture & Technical Design

## 1. Overview & Core Philosophy

The **AI Crop Disease Detection & Outbreak Risk Prediction System** is a production-grade, 100% software-based agricultural advisory platform. The architecture is purposefully decoupled into five autonomous layers:

1. **ML Training & Optimization Pipeline (`ml/`)**: PyTorch-based two-stage transfer learning with EfficientNet-B0 / MobileNetV3 backbones, perceptual-hash deduplication, ONNX export, INT8 quantization, temperature calibration, and Grad-CAM explainability.
2. **Core Agronomic Engine (`backend/app/knowledge_base/` & `backend/app/services/risk.py`)**: A rule-based heuristic Outbreak Risk Engine grounded in university extension agronomic thresholds (UC Davis, Cornell, Penn State, FAO, CABI), operating over 38 crop-disease pairs.
3. **Live Microclimate Weather Aggregator (`backend/app/services/weather.py`)**: Asynchronous, rate-limited, and TTL-cached client querying Open-Meteo historical (7-day past) and forecast (7-day future) meteorological metrics.
4. **Backend API Service (`backend/app/`)**: High-performance asynchronous FastAPI service with SQLAlchemy 2.x ORM, Alembic migrations, JWT Bearer authentication, SlowAPI rate-limiting, Prometheus instrumentation, and ONNX Runtime CPU-optimized inference.
5. **Farmer-Centric Frontend (`frontend/`)**: Mobile-first, responsive React 18 + TypeScript + Tailwind CSS application featuring offline resilience, client-side image compression, i18n support, interactive risk gauges, and action checklists.

---

## 2. End-to-End System Architecture Diagram

```mermaid
graph TD
    subgraph Client ["Client Layer (Farmer / Agronomist)"]
        UI["React 18 PWA / Web Client"]
        Cam["Mobile Camera / Leaf Upload"]
        Loc["Geolocation API / City Search"]
    end

    subgraph Edge ["Edge & Reverse Proxy"]
        Nginx["Nginx Web Server (:80)"]
    end

    subgraph API ["Backend Service (FastAPI :8000)"]
        Router["API Gateway / Router (/api/v1)"]
        AuthMiddleware["JWT Auth & Rate Limiter (SlowAPI)"]
        ImageProc["EXIF Stripping & Preprocessing (Pillow)"]
        InferenceSvc["ONNX Runtime Engine (Int8 / FP32)"]
        WeatherSvc["Open-Meteo Weather Client (Async httpx + TTL Cache)"]
        RiskEngine["Agronomic Heuristic Risk Engine (0-100)"]
        KBSvc["Curated Knowledge Base (38 Classes)"]
    end

    subgraph Storage ["Data & Model Storage"]
        Postgres[(PostgreSQL / SQLite Database)]
        ModelFile[("ONNX Model / labels.json")]
        DiskUploads[("Sanitized Leaf Storage")]
        ReportsDir[("ml/reports/*.json")]
    end

    subgraph External ["Public Environmental Data"]
        OpenMeteo["Open-Meteo Forecast & History APIs"]
        GeoAPI["Open-Meteo Geocoding API"]
    end

    subgraph Observability ["Telemetry & Monitoring"]
        Prometheus["Prometheus Server (:9090)"]
    end

    Cam --> UI
    Loc --> UI
    UI -->|HTTPS / REST API| Nginx
    Nginx -->|Proxy /api/| Router
    Router --> AuthMiddleware
    AuthMiddleware --> ImageProc
    ImageProc --> DiskUploads
    ImageProc --> InferenceSvc
    InferenceSvc --> ModelFile
    Router --> WeatherSvc
    WeatherSvc --> OpenMeteo
    WeatherSvc --> GeoAPI
    InferenceSvc --> RiskEngine
    WeatherSvc --> RiskEngine
    KBSvc --> RiskEngine
    Router --> Postgres
    Router --> Prometheus
    Router --> ReportsDir
```

---

## 3. Detailed Request-Response Pipeline

When a farmer captures and submits a crop photo through the web interface, the following sequence executes:

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as Farmer (Browser)
    participant Client as React Client
    participant API as FastAPI Backend
    participant Img as Image Privacy Service
    participant ONNX as ONNX Runtime Engine
    participant Weather as Open-Meteo Client
    participant Risk as Outbreak Risk Engine
    participant DB as Database (Postgres)

    Farmer->>Client: Capture Leaf Photo & Select Location
    Client->>Client: Client-side downscale (max 1280px)
    Client->>API: POST /api/v1/analyze (Multipart Image + Lat/Lon)
    API->>Img: Validate MIME, size, & strip EXIF metadata
    Img-->>API: Clean JPEG saved to disk & RGB Tensor
    
    par Inference & Weather
        API->>ONNX: Run Softmax + Temperature-scaled Inference
        ONNX-->>API: Top-3 Classes + Confidences + Entropy
    and Environmental Fetch
        API->>Weather: Fetch Past 7d + Next 7d Microclimate
        Weather-->>API: Hourly Temp, RH, Rain, High Humidity Hours
    end

    API->>Risk: Evaluate Agronomic Rules (Disease x Weather)
    Risk-->>API: Risk Score (0-100), Level, Contributing Factors, 7-Day Outlook
    API->>DB: Store Analysis Record (JSON Snapshots)
    API-->>Client: Return Disease, Confidences, Risk Assessment, & Curated Actions
    Client-->>Farmer: Render Farmer-Friendly Result Card & Checklists
```

---

## 4. Key Architectural Design Decisions

### A. ONNX Runtime over PyTorch in Production
- **Decision**: Export PyTorch model to ONNX and serve inference exclusively via `onnxruntime` CPU engine in production.
- **Rationale**: Reduces Docker image size from >4.5 GB (PyTorch + CUDA) to <350 MB (slim Python + onnxruntime CPU). Cuts container memory footprint from 1.2 GB to ~85 MB per worker, eliminating GPU dependencies while maintaining sub-15ms inference latency.

### B. Transparent Heuristic Risk Engine vs Black-box ML
- **Decision**: Implement outbreak risk prediction as a deterministic, auditable rule engine based on peer-reviewed agronomic temperature, humidity, and leaf-wetness thresholds rather than training an ML model on synthetic labels.
- **Rationale**: There is no verified, labeled outbreak ground truth for smallholder farms globally. A transparent heuristic provides farmers with explainable causal factors (e.g., "72 hours above 85% RH") rather than uninterpretable black-box probabilities.

### C. Farmer Privacy by Design (EXIF Stripping)
- **Decision**: All uploaded images undergo complete EXIF metadata destruction before disk persistence.
- **Rationale**: Raw smartphone photos embed precise GPS coordinates, device identifiers, and timestamps. EXIF stripping prevents involuntary geolocation leakage while allowing farmers to explicitly share coordinates only when requesting weather risk assessments.

### D. Multi-Tiered Weather Caching & Fallback
- **Decision**: Implement in-memory TTL caching (1 hour) keyed on coordinates rounded to 3 decimal places (~110m resolution), coupled with a deterministic agronomic fallback generator if external APIs are unreachable.
- **Rationale**: Prevents API rate-limiting, minimizes network latency, and ensures zero downtime during rural connectivity drops.
