# AI Disease Diagnosis System

Complete full-stack AI-powered disease diagnosis application using Next.js 14 + Python FastAPI + Machine Learning.

## Tech Stack

- **Frontend:** Next.js 14 (App Router) + Tailwind CSS
- **Backend:** Next.js API Routes + Python FastAPI
- **AI/ML:** Scikit-learn Logistic Regression
- **Data:** CSV dataset with 30+ diseases

## Quick Start

### Step 1: Install Dependencies

```bash
npm install
```

### Step 2: Install Python Dependencies

```bash
pip install -r lib/requirements.txt
```

### Step 3: Train the AI Model

```bash
cd lib
python model.py
```

This will create `disease_model.pkl` file.

### Step 4: Start Python API Server

```bash
python lib/predict.py
```

Server runs on `http://localhost:8000`

### Step 5: Start Next.js Frontend (New Terminal)

```bash
npm run dev
```

Frontend runs on `http://localhost:3000`

### Step 6: Open Browser

Go to `http://localhost:3000` and start diagnosing!

## Usage

1. Enter symptoms separated by commas
   ```
   Example: fever, cough, headache
   ```

2. Click "Diagnose" button

3. View top 3 predicted diseases with:
   - Confidence percentage
   - Matched symptoms
   - Recommendations

## Project Structure

```
├── app/
│   ├── layout.js           # Root layout
│   ├── page.js             # Main homepage
│   ├── globals.css         # Tailwind styles
│   └── api/
│       └── predict/
│           └── route.js    # Next.js API endpoint
├── lib/
│   ├── model.py           # Train AI model
│   ├── predict.py         # FastAPI server
│   ├── requirements.txt   # Python dependencies
│   └── disease_model.pkl  # Trained model (generated)
├── data/
│   ├── symptoms_disease.csv    # Dataset
│   └── knowledge-base.json     # Recommendations
├── public/                # Static assets
├── package.json
└── README.md
```

## API Endpoints

### Next.js API

**POST** `/api/predict`
```json
{
  "symptoms": "fever, cough, headache"
}
```

**Response:**
```json
{
  "predictions": [
    {
      "disease": "Flu",
      "confidence": 0.85,
      "matched_symptoms": ["fever", "cough", "headache"],
      "recommendation": "Rest, drink fluids..."
    }
  ]
}
```

### Python FastAPI

**POST** `http://localhost:8000/predict`

**GET** `http://localhost:8000/` - Health check

## Dataset

Located at `data/symptoms_disease.csv`

Contains 30+ diseases including:
- Flu, Cold, COVID-19
- Diabetes, Hypertension
- Migraine, Asthma
- And more...

## Model Details

- **Algorithm:** Logistic Regression (Multinomial)
- **Features:** Symptom text vectorization
- **Training:** 80/20 train-test split
- **Accuracy:** ~85%
- **Output:** Top 3 diseases with probabilities

## Development Tips

**Hot Reload:**
- Next.js auto-reloads on file changes
- Restart Python server after model changes

**Add New Diseases:**
1. Edit `data/symptoms_disease.csv`
2. Add recommendation to `data/knowledge-base.json`
3. Retrain model: `python lib/model.py`
4. Restart Python server

**Debugging:**
- Check Python server logs at port 8000
- Check Next.js console for API errors
- Ensure both servers are running

## Deployment

### Deploy Frontend (Vercel)

```bash
npm run build
vercel deploy
```

Set environment variable:
```
PYTHON_API_URL=https://your-python-api.com
```

### Deploy Python API (Railway/Render)

Use `lib/predict.py` as entry point

```bash
uvicorn lib.predict:app --host 0.0.0.0 --port 8000
```
