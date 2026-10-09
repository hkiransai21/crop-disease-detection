# Backend REST API Specification

The API is served under the `/api/v1` prefix. Interactive Swagger/OpenAPI documentation is available at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

---

## 1. Authentication & Security

- **Scheme**: Bearer JWT (`Authorization: Bearer <access_token>`)
- **Tokens**: Access tokens expire in 60 minutes. Refresh tokens expire in 7 days.
- **Rate Limits**:
  - Auth routes (`/auth/register`, `/auth/login`, `/auth/refresh`): 10 requests / minute
  - Analysis route (`/analyze`): 20 requests / minute

---

## 2. Endpoints Summary

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | None | Register new farmer account |
| `POST` | `/api/v1/auth/login` | None | Authenticate and obtain JWT tokens |
| `POST` | `/api/v1/auth/refresh` | None | Refresh access token using refresh token |
| `GET` | `/api/v1/auth/me` | Bearer | Get authenticated user profile |
| `DELETE` | `/api/v1/auth/me` | Bearer | Delete account and all diagnosis records |
| `POST` | `/api/v1/analyze` | Optional | Upload leaf photo for disease & risk analysis |
| `GET` | `/api/v1/history` | Bearer | List user's diagnosis history |
| `GET` | `/api/v1/history/{id}` | Bearer | Retrieve detailed analysis record |
| `DELETE` | `/api/v1/history/{id}` | Bearer | Delete analysis record |
| `POST` | `/api/v1/history/{id}/feedback` | Bearer | Submit diagnostic accuracy feedback |
| `GET` | `/api/v1/diseases` | None | List knowledge base diseases (filter by crop/query) |
| `GET` | `/api/v1/diseases/{id}` | None | Get detailed disease entry and agronomic guide |
| `GET` | `/api/v1/weather` | None | Get 14-day weather summary for coordinates |
| `GET` | `/api/v1/geocode` | None | Search locations by name via Open-Meteo |
| `GET` | `/api/v1/health` | None | Liveness health check |
| `GET` | `/api/v1/ready` | None | Readiness check (model loaded & db connected) |
| `GET` | `/api/v1/model/info` | None | Model version, metadata, and measured metrics |
| `GET` | `/api/v1/metrics` | None | Prometheus telemetry metrics |

---

## 3. Core Endpoint Examples

### `POST /api/v1/analyze`
**Request**: `multipart/form-data`
- `image`: Binary file (`image/jpeg`, `image/png`, `image/webp`, max 10MB)
- `latitude` (optional): Float (-90.0 to 90.0)
- `longitude` (optional): Float (-180.0 to 180.0)
- `manual_temp_c` (optional): Float
- `manual_humidity_pct` (optional): Float
- `manual_recent_rain` (optional): Boolean

**Response (200 OK)**:
```json
{
  "id": "e4b3c2a1-1234-5678-9abc-def012345678",
  "predicted_label": "Tomato___Early_blight",
  "crop": "Tomato",
  "disease_name": "Early Blight",
  "scientific_name": "Alternaria solani",
  "confidence": 0.942,
  "is_uncertain": false,
  "top_k": [
    {
      "class_name": "Tomato___Early_blight",
      "crop": "Tomato",
      "disease_name": "Early Blight",
      "confidence": 0.942,
      "percentage": "94.2%"
    },
    {
      "class_name": "Tomato___Target_Spot",
      "crop": "Tomato",
      "disease_name": "Target Spot",
      "confidence": 0.038,
      "percentage": "3.8%"
    },
    {
      "class_name": "Tomato___Septoria_leaf_spot",
      "crop": "Tomato",
      "disease_name": "Septoria Leaf Spot",
      "confidence": 0.012,
      "percentage": "1.2%"
    }
  ],
  "risk_assessment": {
    "overall_risk_score": 78,
    "overall_risk_level": "HIGH",
    "crop": "Tomato",
    "evaluated_disease": "Early Blight",
    "summary": "Weather conditions over the past week and forecast period strongly favor Early Blight infection and spread.",
    "contributing_factors": [
      "High relative humidity recorded for 42 hours over the last 7 days",
      "Mean ambient temperature (24.2°C) falls squarely within the pathogen's optimal proliferation range (24°C - 29°C)",
      "Total past rainfall (12.4mm) created favorable free-moisture on leaf surfaces"
    ],
    "daily_outlook": [
      {
        "date": "2026-10-07",
        "temp_mean_c": 23.5,
        "humidity_mean_pct": 82.0,
        "precipitation_mm": 4.5,
        "risk_level": "HIGH",
        "notes": "Rainfall and 82% humidity provide prime spore germination conditions."
      }
    ],
    "disclaimer": "Advisory estimate based on agronomic microclimate rules. Not a validated meteorological outbreak forecast."
  },
  "recommendations": {
    "prevention_steps": [
      "Prune lower leaves that contact the soil surface to prevent soil-splash inoculation",
      "Implement drip or furrow irrigation to keep foliage dry during overhead watering",
      "Practice minimum 2-year crop rotation with non-solanaceous crops"
    ],
    "organic_controls": [
      "Apply Bacillus subtilis bio-fungicide at first symptom appearance",
      "Use approved fixed-copper formulations during humid periods"
    ],
    "chemical_controls": [
      "Broad-spectrum protective fungicides (e.g. Chlorothalonil, Mancozeb) - consult local extension label requirements"
    ],
    "severity": "HIGH",
    "when_to_consult_expert": "Consult your local county extension officer if lesion defoliation exceeds 25% of canopy.",
    "safety_notes": [
      "Always read and strictly follow pesticide product label instructions before application",
      "Wear mandatory Personal Protective Equipment (PPE): nitrile gloves, respirator, eye protection, and long sleeves",
      "Adhere strictly to Pre-Harvest Intervals (PHI) and Re-Entry Intervals (REI)",
      "Consult local agricultural extension authorities for region-specific chemical permits and regulations"
    ],
    "sources": [
      "University of California Statewide Integrated Pest Management Program (UC IPM) - Tomato Early Blight",
      "Cornell University Cooperative Extension - Vegetable MD Online"
    ]
  },
  "weather_snapshot": {
    "current_temp_c": 22.5,
    "current_humidity_pct": 78.0,
    "past_7d_total_rain_mm": 12.4,
    "data_source": "Open-Meteo API",
    "is_live": true
  },
  "image_path": "/uploads/e4b3c2a1-1234-5678-9abc-def012345678.jpg",
  "created_at": "2026-10-06T20:30:00Z"
}
```
