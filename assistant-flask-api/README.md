# Phi-3 LoRA Adapter API

A Flask API application that loads the local Phi-3 Mini model with dynamic LoRA adapter support. The API provides inference endpoints for job matching, resume evaluation, LaTeX resume generation, and recruiter dialog.

## 🏗️ Architecture

- **Base Model**: Phi-3-mini-4k-instruct (loaded at startup with 4-bit quantization)
- **LoRA Adapters**: Four specialized adapters for different tasks
- **Framework**: Flask with CORS support
- **Quantization**: 4-bit NF4 quantization for memory efficiency
- **Concurrency**: Thread-safe inference with locks
- **Deployment**: WSGI-compatible (gunicorn/uvicorn ready)

## 📁 Project Structure

```
api/
├── app.py                 # Main Flask application with endpoints
├── model_loader.py       # Model loading with 4-bit quantization
├── adapters.py           # LoRA adapter management
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the API

```bash
cd api/
python app.py
```

The API will start on `http://localhost:5000`

### 3. Health Check

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "adapters_ready": true
}
```

## 📚 API Endpoints

### Health Check
**GET** `/health`
- Returns model and adapter status
- Used to verify the API is running

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "adapters_ready": true
}
```

### List Available Adapters
**GET** `/adapters`
- Lists all available LoRA adapters

**Response:**
```json
{
  "available_adapters": ["job_match", "resume_eval", "latex_resume", "recruiter_dialog"],
  "count": 4
}
```

### Job Matching
**POST** `/run/job_match`

Analyzes resume compatibility with job offers.

**Request Body:**
```json
{
  "resume_json": {
    "name": "John Doe",
    "email": "john@example.com",
    "experience": [...],
    "skills": [...]
  },
  "job_offers_json": [
    {
      "title": "Senior ML Engineer",
      "company": "Tech Corp",
      "requirements": [...]
    }
  ]
}
```

**Response:**
```json
{
  "adapter": "job_match",
  "response": "Based on the resume and job offers...",
  "status": "success"
}
```

### Resume Evaluation
**POST** `/run/resume_eval`

Provides feedback and suggestions for resume improvement.

**Request Body:**
```json
{
  "resume_json": {
    "name": "John Doe",
    "email": "john@example.com",
    "experience": [...],
    "skills": [...]
  }
}
```

**Response:**
```json
{
  "adapter": "resume_eval",
  "response": "Your resume is well-structured. Here are some suggestions...",
  "status": "success"
}
```

### LaTeX Resume Generation
**POST** `/run/latex_resume`

Converts resume data to LaTeX format.

**Request Body:**
```json
{
  "resume_json": {
    "name": "John Doe",
    "email": "john@example.com",
    "experience": [...],
    "skills": [...]
  }
}
```

**Response:**
```json
{
  "adapter": "latex_resume",
  "response": "\\documentclass{article}\\n\\begin{document}\\n...",
  "status": "success"
}
```

### Recruiter Dialog
**POST** `/run/recruiter_dialog`

Interactive recruiter AI for HR conversations.

**Request Body:**
```json
{
  "message": "What are the key skills needed for this role?"
}
```

**Response:**
```json
{
  "adapter": "recruiter_dialog",
  "response": "The key skills needed for this role include...",
  "status": "success"
}
```

## ⚙️ Configuration

Environment variables (optional):

```bash
# Path to the base model directory
export BASE_MODEL_PATH="../Phi-3-mini-4k-instruct"

# Path to the adapters directory
export ADAPTERS_BASE_PATH="../lora_adapters"

# Maximum tokens for generation
export MAX_NEW_TOKENS="512"

# Temperature for sampling
export TEMPERATURE="0.7"
```

## 🔧 Advanced Usage

### Running with Gunicorn (Production)

For production deployment with multiple worker processes:

```bash
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With custom configurations
gunicorn -w 4 \
  -b 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  app:app
```

### Running with Uvicorn (ASGI)

If converting to async:

```bash
pip install uvicorn

uvicorn app:app --host 0.0.0.0 --port 5000 --workers 4
```

## 🌐 Exposing to the Internet

### Option 1: Using ngrok (Free, Quick)

1. **Install ngrok:**
   ```bash
   # Download from https://ngrok.com/download
   # or with package manager
   ```

2. **Start your Flask API:**
   ```bash
   cd api/
   python app.py
   ```

3. **In a new terminal, expose via ngrok:**
   ```bash
   ngrok http 5000
   ```

4. **You'll see output like:**
   ```
   Forwarding     https://abc123.ngrok.io -> http://localhost:5000
   ```

5. **Access the API externally:**
   ```bash
   curl https://abc123.ngrok.io/health
   ```

**Advantages:**
- No infrastructure setup needed
- Instant public HTTPS URL
- Great for testing/demos

**Limitations:**
- URL changes on each restart (unless paid plan)
- Rate limited on free tier
- Not for production

### Option 2: Reverse Proxy with Nginx

1. **Install Nginx:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install nginx
   
   # macOS
   brew install nginx
   ```

2. **Configure Nginx:**
   Create `/etc/nginx/sites-available/phi-api`:
   
   ```nginx
   upstream flask_app {
       server localhost:5000;
   }

   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://flask_app;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable the site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/phi-api /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **Add HTTPS with Let's Encrypt:**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Option 3: Azure Container App (Production)

1. **Create Azure Resources:**
   ```bash
   # Set variables
   RESOURCE_GROUP="phi-api-rg"
   LOCATION="eastus"
   
   # Create resource group
   az group create -n $RESOURCE_GROUP -l $LOCATION
   
   # Create container registry
   az acr create -g $RESOURCE_GROUP -n phiapiregistry --sku Basic
   ```

2. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.10-slim

   WORKDIR /app

   # Copy requirements
   COPY api/requirements.txt .

   # Install dependencies
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application
   COPY . .

   # Expose port
   EXPOSE 5000

   # Set working directory
   WORKDIR /app/api

   # Run application
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

3. **Build and Push to ACR:**
   ```bash
   az acr build -r phiapiregistry -t phi-api:latest .
   ```

4. **Deploy to Container App:**
   ```bash
   az containerapp create \
     -n phi-api \
     -g $RESOURCE_GROUP \
     --image phiapiregistry.azurecr.io/phi-api:latest \
     --cpu 2 \
     --memory 4Gi \
     --ingress external \
     --target-port 5000 \
     --registry-server phiapiregistry.azurecr.io \
     --registry-username <username> \
     --registry-password <password>
   ```

5. **Get public URL:**
   ```bash
   az containerapp show -n phi-api -g $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn"
   ```

## 🔐 Security Considerations
# Phi-3 LoRA Adapter API — Short Guide

Lightweight Flask API that serves a local Phi-3 Mini model with on-demand LoRA adapters.

Quick highlights
- Single base model loaded once; LoRA adapters applied dynamically via PEFT.
- Endpoints: `/health`, `/adapters`, `/run/<adapter>`, and unified `/assistant`.
- Designed to run locally (GPU if available) and expose via ngrok or reverse proxy for external access.

Quick start
1. Install deps and run:

```powershell
pip install -r requirements.txt
cd api
python app.py
```

2. Health check:

```powershell
curl http://localhost:5000/health
```

Core endpoints (short)
- `GET /health` — returns service, model and adapter status.
- `GET /adapters` — lists available LoRA adapters under `lora_adapters/`.
- `POST /run/<adapter>` — run a specific adapter (name like `job_match`, `resume_eval`, `latex_resume`, `recruiter_dialog`).
  - Body: adapter-specific JSON (e.g. `resume_json`, `job_offers_json`, or `message`).
- `POST /assistant` — unified chat: `{message, context?, resume_json?, job_offers_json?}`; the router picks base model, career prompt, or an adapter.

Minimal examples
```powershell
# Health
curl http://localhost:5000/health

# Job match
curl -X POST http://localhost:5000/run/job_match -H "Content-Type: application/json" -d '{"resume_json": {"name": "Alice"}, "job_offers_json": [{"title":"ML Engineer"}]}'

# Assistant (career)
curl -X POST http://localhost:5000/assistant -H "Content-Type: application/json" -d '{"message": "How can I improve my chances for ML roles?"}'
```

Notes
- Ensure `BASE_MODEL_PATH` and `ADAPTERS_BASE_PATH` (if used) point to local folders. The server uses GPU when available.
- For production, run under Gunicorn/ASGI behind a reverse proxy; secure the API with auth and rate limits.

That's it — concise, local-first API for quick experiments with Phi-3 and LoRA adapters.
**Solution**:
