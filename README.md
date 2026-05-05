# 🧠 NeferSurvey — Survey Intelligence Engine


## Overview

NeferSurvey is an enterprise-grade customer feedback intelligence platform that automatically analyzes textual feedback using AI. It classifies sentiment, detects emotions, extracts key issues, and presents live insights through a professional Grafana dashboard embedded inside a Gradio web interface.

---

## Features

| Feature | Description |
|---|---|
| 🤖 AI Analysis | Groq LLM classifies sentiment, emotion, key issue, and urgency |
| 📊 Live Dashboard | Grafana dashboard with real-time charts and panels |
| 📁 Bulk Upload | Upload CSV or TXT files with hundreds of feedback entries |
| 💬 RAG Q&A | Ask questions grounded strictly in stored feedback |
| 🔍 Vector Search | FAISS cosine similarity search for relevant feedback retrieval |
| 🔌 REST API | FastAPI server exposing all data endpoints for Grafana |
| 🗄️ Persistent Storage | SQLite database storing all feedback with embeddings |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Gradio UI (:7860)                     │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────┐ │
│  │Submit       │ │Bulk Upload   │ │Ask the Data (RAG) │ │
│  │Feedback     │ │CSV / TXT     │ │Q&A Engine         │ │
│  └──────┬──────┘ └──────┬───────┘ └─────────┬─────────┘ │
└─────────┼───────────────┼───────────────────┼───────────┘
          │               │                   │
          ▼               ▼                   ▼
┌─────────────────┐  ┌─────────┐   ┌──────────────────┐
│ Sentiment Engine│  │ SQLite  │   │ Embedding Engine  │
│ Groq LLM API    │  │  DB     │   │ FAISS + MiniLM    │
└─────────────────┘  └────┬────┘   └──────────────────┘
                          │
                          ▼
               ┌──────────────────┐
               │ FastAPI Server   │
               │   (:8000)        │
               └────────┬─────────┘
                        │
                        ▼
               ┌──────────────────┐
               │ Grafana Dashboard│
               │   (:3000)        │
               └──────────────────┘
```

---

## Project Structure

```
NeferSurvey/
├── .env                    
├── config.py               
├── database.py             
├── sentiment_engine.py     
├── embedding_engine.py     
├── insight_aggregator.py   
├── qa_engine.py            
├── api_server.py           
├── ui.py                   
├── requirements.txt        
└── nefersurvey.db          
```


## Installation

### Step 1: Clone or create the project folder
```
NeferSurvey/
```

### Step 2: Install Python dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Create `.env` file
```env
GROQ_API_KEY=your_groq_api_key_here
```
Get your free API key from: https://console.groq.com

### Step 4: Install Grafana
Download from: https://grafana.com/grafana/download?platform=windows
Run the `.msi` installer with default settings.

### Step 5: Install Grafana Infinity Plugin
Run in CMD as Administrator:
```cmd
"C:\Program Files\GrafanaLabs\grafana\bin\grafana-cli.exe" --homepath "C:\Program Files\GrafanaLabs\grafana" plugins install yesoreyeram-infinity-datasource
net stop Grafana
net start Grafana
```

### Step 6: Configure Grafana for embedding
Create file: `C:\Program Files\GrafanaLabs\grafana\conf\custom.ini`
```ini
[security]
allow_embedding = true
cookie_samesite = disabled

[auth.anonymous]
enabled = true
org_name = Main Org.
org_role = Viewer
```
Restart Grafana after saving.

---

## Configuration

All settings are in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | LLM model for analysis |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `TOP_K_RESULTS` | `5` | Number of feedback entries retrieved for Q&A |
| `MAX_FEEDBACK_LENGTH` | `2000` | Max characters per feedback entry |
| `DB_PATH` | `nefersurvey.db` | SQLite database file path |

---

## Running the System

### Step 1: Start Grafana (CMD as Administrator)
```cmd
net start Grafana
```

### Step 2: Start API Server (Terminal 1)
```powershell
cd D:\Neferx\NeferSurvey
python api_server.py
```
Wait for: `INFO: Uvicorn running on http://0.0.0.0:8000`

### Step 3: Start Gradio UI (Terminal 2)
```powershell
cd D:\Neferx\NeferSurvey
python ui.py
```
Wait for: `Running on local URL: http://0.0.0.0:7860`

### Step 4: Open in browser

| Service | URL |
|---|---|
| 🤖 Gradio UI | http://localhost:7860 |
| 📊 Grafana Dashboard | http://localhost:3000 |
| 🔌 API Docs | http://localhost:8000/docs |

### Stop everything
```powershell
# Press Ctrl+C in each terminal
# Stop Grafana:
net stop Grafana
```

---

## How to Use

### Submit Single Feedback
1. Go to **📝 Submit Feedback** tab
2. Type or paste customer feedback
3. Click **🚀 Analyze & Submit**
4. View sentiment, emotion, key issue, and urgency results

### Bulk Upload
1. Go to **📁 Bulk Upload** tab
2. Prepare a CSV file with a column named `feedback`
3. Upload the file and click **📤 Process File**
4. Monitor the processing log in real time

### View Dashboard
1. Go to **📊 Dashboard** tab
2. The Grafana dashboard loads automatically
3. Click **🔄 Refresh Dashboard** after submitting new feedback

### Ask Questions (RAG)
1. Go to **💬 Ask the Data** tab
2. Type a question about the feedback data
3. Click **🔍 Ask**
4. Receive a grounded answer citing exact Feedback IDs



## Dashboard Panels

| Panel | Type | Data Source |
|---|---|---|
| Sentiment Distribution | Pie Chart | `/sentiment-distribution` |
| Top Feedbacks | Bar Chart | `/top-issues` |
| Emotion Distribution | Bar Chart | `/emotion-distribution` |
| Urgency Breakdown | Bar Chart | `/urgency` |
| Total Feedback | Stat | `/total-feedback` |
| Dominant Sentiment | Stat | `/dominant-sentiment` |
| Top Emotion | Stat | `/top-emotion` |
| All Feedback | Table | `/feedback` |

---

## RAG Q&A Engine

The Q&A module uses Retrieval-Augmented Generation to ensure all answers are grounded in real feedback data:

```
User Question
     │
     ▼
Generate Embedding (MiniLM)
     │
     ▼
FAISS Cosine Similarity Search
     │
     ▼
Retrieve Top-5 Relevant Feedback
     │
     ▼
Build Grounded Prompt
     │
     ▼
Groq LLM (temperature=0.1)
     │
     ▼
Answer citing exact Feedback IDs
```



## Troubleshooting

| Problem | Solution |
|---|---|
| `GROQ_API_KEY not found` | Check `.env` file exists and key is correct |
| `Grafana not loading` | Run `net start Grafana` in Admin CMD |
| `API server not starting` | Make sure port 8000 is free |
| `No data in dashboard` | Submit feedback first, then refresh |
| `Q&A returns no results` | Upload feedback via Bulk Upload first |
| `Iframe blocked in Gradio` | Check `custom.ini` has `allow_embedding = true` |
| `Port 7860 in use` | Kill existing process or change port in `ui.py` |

---

