"""
FastAPI server for disease prediction with Gemini fallback.
Handles both structured (comma-separated) and free-form symptom input.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np
import json
import os
import requests
import re
from typing import List, Dict, Any

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and knowledge base at startup
print("Loading AI model...")
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(base_dir, 'lib', 'disease_model.pkl')

try:
    model_data = joblib.load(model_path)
    model = model_data['model']
    symptom_cols = model_data['symptom_cols']
    symptom_vocab = set(model_data['symptom_vocab'])
    print(f"✅ AI model loaded successfully")
    print(f"✅ Recognizes {len(symptom_vocab)} symptoms")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    symptom_cols = []
    symptom_vocab = set()

print("Loading knowledge base...")
knowledge_path = os.path.join(base_dir, 'data', 'knowledge-base.json')
try:
    with open(knowledge_path, 'r') as f:
        knowledge = json.load(f)
except Exception as e:
    print(f"❌ Error loading knowledge base: {e}")
    knowledge = {"recommendations": {"default": "Consult a healthcare professional."}}

# Gemini API configuration
GEMINI_API_KEY = "AIzaSyDNeeL4fMV_R2yaPzbhgt8zSkjLI78t4x8"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# ============= Helper Functions =============

def extract_symptoms_from_text(user_input: str) -> List[str]:
    """Extract symptom keywords from free-form text."""
    user_input_lower = user_input.lower()
    extracted = []
    
    symptom_patterns = {
        'pain': ['pain', 'ache', 'hurt', 'sore', 'aching'],
        'fever': ['fever', 'high temperature', 'hot', 'temperature'],
        'cough': ['cough', 'coughing'],
        'headache': ['headache', 'head pain', 'migraine'],
        'nausea': ['nausea', 'nauseous', 'feel sick'],
        'vomiting': ['vomit', 'vomiting'],
        'fatigue': ['fatigue', 'tired', 'exhausted', 'exhaustion', 'weak'],
        'dizziness': ['dizzy', 'dizziness', 'vertigo'],
        'anxiety': ['anxiety', 'anxious', 'nervous', 'feel nervous'],
        'depression': ['depression', 'depressed', 'sad'],
        'insomnia': ['insomnia', 'cannot sleep', 'sleep issue'],
        'body_ache': ['body ache', 'muscle ache', 'joint pain'],
    }
    
    for symptom, keywords in symptom_patterns.items():
        for keyword in keywords:
            if keyword in user_input_lower:
                extracted.append(symptom)
                break
    
    return list(set(extracted))

def call_gemini_api(user_input: str) -> Dict[str, Any]:
    """Call Gemini API for free-form symptom interpretation."""
    try:
        prompt = f"""You are a medical assistant. User describes symptoms: "{user_input}"

Return ONLY valid JSON (no other text):
{{
  "predictions": [
    {{
      "disease": "disease name",
      "confidence": 0.5-0.9,
      "matched_symptoms": ["symptom1", "symptom2"],
      "recommendation": "Consult healthcare professional"
    }}
  ]
}}

Provide 1-3 most likely diseases."""

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Gemini error: {response.status_code}")
            return {"predictions": []}
        
        result = response.json()
        if 'candidates' in result and result['candidates']:
            text = result['candidates'][0]['content']['parts'][0]['text']
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                parsed = json.loads(json_match.group(0))
                return parsed
        
        return {"predictions": []}
    
    except Exception as e:
        print(f"Gemini API exception: {e}")
        return {"predictions": []}

def predict_with_model(all_symptoms: List[str]) -> Dict[str, Any]:
    """Use the trained model to predict diseases."""
    if not model or not symptom_cols:
        return {"predictions": [], "source": "model_unavailable"}
    
    matched = [s for s in all_symptoms if s in symptom_vocab]
    if not matched:
        return {"predictions": [], "source": "no_match"}
    
    # Build input vector
    input_vector = np.zeros(len(symptom_cols))
    for symptom in all_symptoms:
        symptom_normalized = symptom.replace(' ', '_')
        if symptom_normalized in symptom_cols:
            idx = symptom_cols.index(symptom_normalized)
            input_vector[idx] = 1
        elif symptom in symptom_vocab:
            for i, col in enumerate(symptom_cols):
                if col.lower().replace('_', ' ') == symptom:
                    input_vector[i] = 1
                    break
    
    if input_vector.sum() == 0:
        return {"predictions": [], "source": "no_vector"}
    
    # Get predictions
    input_vector = input_vector.reshape(1, -1)
    probabilities = model.predict_proba(input_vector)[0]
    classes = model.classes_
    
    top_indices = np.argsort(probabilities)[-3:][::-1]
    predictions = []
    
    for idx in top_indices:
        if probabilities[idx] > 0.05:
            disease = classes[idx]
            confidence = float(probabilities[idx])
            recommendation = knowledge['recommendations'].get(disease, knowledge['recommendations']['default'])
            
            predictions.append({
                "disease": disease,
                "confidence": round(confidence, 2),
                "matched_symptoms": matched,
                "recommendation": recommendation
            })
    
    return {"predictions": predictions, "source": "model", "confidence": predictions[0]["confidence"] if predictions else 0}

# ============= API Routes =============

@app.get('/')
def health():
    """Health check endpoint."""
    return {
        'status': 'online',
        'service': 'AI Disease Diagnosis API',
        'version': '2.0',
        'symptoms_recognized': len(symptom_vocab)
    }

@app.post('/predict')
async def predict(request: Request):
    """Main prediction endpoint."""
    try:
        data = await request.json()
        user_input = data.get('symptoms', '').strip()
        
        if not user_input:
            return {"predictions": [], "source": "empty"}
        
        print(f"\n📥 Received input: {user_input}")
        
        # Extract symptoms (both structured and free-form)
        extracted = extract_symptoms_from_text(user_input)
        comma_sep = [s.strip().lower() for s in user_input.split(',') if s.strip()]
        all_symptoms = list(set(extracted + comma_sep))
        
        print(f"   Extracted symptoms: {extracted}")
        print(f"   Comma-separated: {comma_sep}")
        print(f"   Combined: {all_symptoms}")
        
        # Try model prediction first
        model_result = predict_with_model(all_symptoms)
        print(f"   Model result: {len(model_result.get('predictions', []))} predictions")
        
        if model_result.get('predictions') and model_result.get('confidence', 0) > 0.3:
            print(f"✅ Returning model predictions")
            return {"predictions": model_result['predictions'], "source": "model"}
        
        # Fallback to Gemini
        print(f"   Trying Gemini API...")
        gemini_result = call_gemini_api(user_input)
        
        if gemini_result.get('predictions'):
            print(f"✅ Returning Gemini predictions: {len(gemini_result['predictions'])}")
            return {"predictions": gemini_result['predictions'], "source": "gemini"}
        
        print(f"⚠️  No predictions found")
        return {"predictions": [], "source": "none"}
    
    except Exception as e:
        import traceback
        print(f"❌ ERROR: {e}")
        print(traceback.format_exc())
        return {"predictions": [], "source": "error", "error": str(e)}

if __name__ == '__main__':
    import uvicorn
    print("\n🚀 Starting FastAPI server on http://0.0.0.0:8000")
    uvicorn.run(app, host='0.0.0.0', port=8000)
