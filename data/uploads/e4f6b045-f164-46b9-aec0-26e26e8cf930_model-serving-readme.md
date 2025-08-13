# 🧠 Model Serving with Rollback Support

A lightweight, self-hostable machine learning model serving API with version control, rollback capability, and real-time monitoring via Prometheus and Grafana.

> A minimal, production-style alternative to Seldon, MLflow, or BentoML — designed for solo developers, fast prototyping, and educational use.

---

## 📌 Overview

This project provides a plug-and-play system for serving machine learning models via a REST API, while allowing:
- Seamless **version switching** and rollback via admin endpoints
- Reproducible predictions with explicit model version targeting
- Real-time **metrics and observability** using Prometheus and Grafana
- Easy extension for teams, CI pipelines, or local research workflows

Unlike heavier tools, this system runs locally or on a single VM with minimal setup—no Kubernetes or cloud account required.

---

## 🎯 Use Cases

- 🔁 **Experiment iteration** — switch between model versions with a single API call  
- 🧪 **A/B testing** — compare accuracy or latency across model versions  
- 🧵 **MLOps education** — understand the building blocks of model deployment  
- 🧰 **Internal tools** — quickly expose models to downstream apps  
- 📊 **Live demos** — serve notebook-trained models in a real API  

---

## 🧰 Features

### ✅ Model Serving
- POST endpoint for real-time predictions  
- Supports any `scikit-learn`, `joblib`, or Pickle-based model  
- Optional version override per request  

### 🔁 Rollback & Versioning
- Admin API to set the **active version** (`v1`, `v2`, etc.)  
- All new requests are routed to the active version  
- Models stored in a clear directory structure (`/models/vX/`)  

### 📊 Monitoring
- **Prometheus metrics**: inference latency, model usage, error counts  
- **Grafana dashboards**: visualize trends and performance  
- `/metrics` endpoint exposed for scraping  

### ⚙️ Configuration
- JSON or `.env` based config for paths, ports, etc.  
- Optional: Redis for shared state across instances  

### 🐳 Deployment
- Dockerized, with `docker-compose.yml` for single-command setup  
- Works locally, on a VPS, or in the cloud  

---

## 🏗️ Project Structure

```
model-serving/
├── app/
│   ├── main.py          # FastAPI app entrypoint
│   ├── predict.py       # Prediction logic and routing
│   ├── model_loader.py  # Model registry and lazy loading
│   ├── admin.py         # Version switching and rollback
│   ├── config.py        # Config parsing
│   └── metrics.py       # Prometheus metrics
├── models/
│   ├── v1/model.pkl
│   └── v2/model.pkl
├── grafana/
│   └── dashboard.json
├── prometheus.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose (optional but recommended)
- `scikit-learn`, `joblib` or compatible ML model

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/model-serving-rollback.git
cd model-serving-rollback
pip install -r requirements.txt
```

### 2. Add a Model

Save a trained model to `models/v1/model.pkl`. Example with `scikit-learn`:

```python
import joblib
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier().fit(X_train, y_train)
joblib.dump(model, 'models/v1/model.pkl')
```

### 3. Run the API

```bash
uvicorn app.main:app --reload
```

Or use Docker:

```bash
docker-compose up --build
```

---

## 🌐 API Reference

### `POST /predict`
**Body:**
```json
{ "features": [1.2, 3.4, 5.6] }
```

**Optional:** `?version=v2`

**Returns:**
```json
{ "prediction": 1, "model_version": "v1" }
```

---

### `POST /admin/set-active-version`

Set active model globally:
```json
{ "version": "v2" }
```

---

### `GET /healthz`

Simple health check.

---

### `GET /metrics`

Prometheus-compatible metrics endpoint.

---

## 📊 Monitoring

### Prometheus

Scrape config included in `prometheus.yml`. Metrics tracked:
- `model_inference_latency_seconds`
- `model_prediction_requests_total`
- `model_prediction_errors_total`
- `model_version_active{version="vX"}`

### Grafana

Import `grafana/dashboard.json` to get a pre-built dashboard with:
- Request volume over time  
- Average latency per model version  
- Active version indicator  

---

## 🧩 Roadmap Ideas

- [ ] Add SQLite or Redis for persistent state across restarts  
- [ ] UI for switching versions  
- [ ] Canary routing (e.g., 90% to v2, 10% to v1)  
- [ ] CI/CD: Deploy models on push via GitHub Actions  
- [ ] Hugging Face/ONNX support  

---

## 🤝 Contributing

Pull requests welcome! Ideas, bugs, and feature requests can be submitted via Issues.

---

## 📄 License

MIT License
