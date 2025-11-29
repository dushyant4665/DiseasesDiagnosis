from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import json
import os
from typing import List
import requests
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading AI model...")
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(base_dir, 'lib', 'disease_model.pkl')
model_data = joblib.load(model_path)
model = model_data['model']
symptom_cols = model_data['symptom_cols']
symptom_vocab = set(model_data['symptom_vocab'])

print("Loading knowledge base...")
knowledge_path = os.path.join(base_dir, 'data', 'knowledge-base.json')
with open(knowledge_path, 'r') as f:
    knowledge = json.load(f)

print("✅ AI model loaded successfully")
print(f"✅ Recognizes {len(symptom_vocab)} symptoms")

# Gemini API configuration
GEMINI_API_KEY = "AIzaSyDNeeL4fMV_R2yaPzbhgt8zSkjLI78t4x8"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def extract_symptoms_from_text(user_input: str) -> List[str]:
    """
    Extract symptom keywords from free-form text like 'pain in neck' or 'feel nervous'.
    Uses regex patterns and common medical terms to identify symptoms.
    """
    user_input_lower = user_input.lower()
    extracted = []
    
    # Common symptom patterns and keywords
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
    
    # Location patterns (e.g., "pain in neck" -> look for neck-related symptoms)
    location_patterns = {
        'neck': ['pain in neck', 'neck pain', 'neck stiffness'],
        'chest': ['pain in chest', 'chest pain', 'chest tightness'],
        'back': ['pain in back', 'back pain', 'lower back'],
        'stomach': ['stomach pain', 'stomach ache', 'abdominal pain', 'belly pain'],
        'head': ['pain in head', 'head pain', 'headache'],
        'throat': ['sore throat', 'throat pain'],
    }
    
    
    # Look for symptom keywords
    for symptom, keywords in symptom_patterns.items():
        for keyword in keywords:
            if keyword in user_input_lower:
                extracted.append(symptom)
                break
    
    # Look for location-based symptoms
    for location, keywords in location_patterns.items():
        for keyword in keywords:
            if keyword in user_input_lower:
                if 'pain' not in extracted:
                    extracted.append('pain')
                break
    
    return list(set(extracted))  # Remove duplicates

def call_gemini_api(user_input: str) -> dict:
    """
    Call Gemini API to interpret free-form symptom description and get disease predictions.
    Falls back when model cannot predict or confidence is low.
    """
    try:
        prompt = f"""You are a professional medical assistant. A patient has described their symptoms as: "{user_input}"

Based on this description, provide ONLY valid JSON output (no other text before or after):
{{
  "predictions": [
    {{
      "disease": "disease name",
      "confidence": 0.6,
      "matched_symptoms": ["symptom1", "symptom2"],
      "recommendation": "Seek medical attention"
    }}
  ]
}}

Rules:
- Provide 1-3 most likely diseases
- Confidence scores between 0.5 and 0.95
- Include symptoms extracted from the description
- Keep recommendations brief and actionable
- IMPORTANT: Output ONLY JSON, no other text"""

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        headers = {"Content-Type": "application/json"}
        
        print(f"   Calling Gemini API...")
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers=headers,
            timeout=15
        )
        
        print(f"   Gemini HTTP Status: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = response.text[:200]
            print(f"   ❌ Gemini API error: {response.status_code} - {error_msg}")
            return {"predictions": []}
        
        result = response.json()
        print(f"   ✅ Got Gemini response")
        
        # Parse Gemini response
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0].get('content', {})
            if 'parts' in content and len(content['parts']) > 0:
                text = content['parts'][0].get('text', '')
                print(f"   Extracted text: {text[:100]}...")
                
                # Extract JSON from response
                try:
                    # Find JSON in the text - look for { } pattern
                    json_match = re.search(r'\{[\s\S]*\}', text)
                    if json_match:
                        json_str = json_match.group(0)
                        parsed = json.loads(json_str)
                        print(f"   ✅ Parsed JSON successfully: {len(parsed.get('predictions', []))} predictions")
                        return parsed
                    else:
                        print(f"   ❌ No JSON found in response: {text[:100]}")
                except json.JSONDecodeError as je:
                    print(f"   ❌ Failed to parse JSON: {str(je)}")
                    return {"predictions": []}
        
        print(f"   ❌ No content in Gemini response")
        return {"predictions": []}
    
    except requests.exceptions.Timeout:
        print(f"   ❌ Gemini API timeout (15s)")
        return {"predictions": []}
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Gemini API connection error")
        return {"predictions": []}
    except Exception as e:
        print(f"   ❌ Gemini API exception: {str(e)}")
        return {"predictions": []}

class PredictRequest(BaseModel):
    symptoms: str

@app.post('/predict')
async def predict(request_data: dict):
    try:
        user_input = request_data.get('symptoms', '').strip()
        
        if not user_input:
            return {"predictions": [], "source": "model"}
        
        # Step 1: Try to extract symptoms from free-form text
        extracted_symptoms = extract_symptoms_from_text(user_input)
        print(f"Extracted symptoms: {extracted_symptoms}")
        
        # Step 2: Also try comma-separated parsing (for backward compatibility)
        comma_separated = [s.strip().lower() for s in user_input.split(',') if s.strip()]
        print(f"Comma-separated symptoms: {comma_separated}")
        
        # Combine both approaches
        all_symptoms = list(set(extracted_symptoms + comma_separated))
        print(f"All symptoms combined: {all_symptoms}")
        
        # Step 3: Match symptoms against the model's vocabulary
        matched = [s for s in all_symptoms if s in symptom_vocab]
        print(f"Matched symptoms: {matched}")
        
        # Step 4: Try model prediction if we have matches
        if matched:
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
            
            if input_vector.sum() > 0:
                input_vector = input_vector.reshape(1, -1)
                probabilities = model.predict_proba(input_vector)[0]
                classes = model.classes_
                
                top_indices = np.argsort(probabilities)[-3:][::-1]
                
                predictions = []
                for idx in top_indices:
                    if probabilities[idx] > 0.05:
                        disease = classes[idx]
                        confidence = float(probabilities[idx])
                        
                        recommendation = knowledge['recommendations'].get(
                            disease, 
                            knowledge['recommendations']['default']
                        )
                        
                        predictions.append({
                            "disease": disease,
                            "confidence": round(confidence, 2),
                            "matched_symptoms": matched,
                            "recommendation": recommendation
                        })
                
                # Return model predictions if confidence is good
                if predictions and predictions[0]["confidence"] > 0.25:
                    print(f"✅ Returning model predictions: {len(predictions)} diseases")
                    return {"predictions": predictions, "source": "model"}
                else:
                    print(f"⚠️  Model confidence too low ({predictions[0]['confidence'] if predictions else 0}), trying Gemini...")
        
        # Step 5: Fallback to Gemini API for free-form or low-confidence inputs
        print(f"🔄 Falling back to Gemini API for input: {user_input}")
        gemini_result = call_gemini_api(user_input)
        print(f"📊 Gemini result: {gemini_result}")
        
        if gemini_result.get('predictions') and len(gemini_result.get('predictions', [])) > 0:
            # Gemini already returns predictions in the right format
            print(f"✅ Returning Gemini predictions: {len(gemini_result.get('predictions', []))} diseases")
            return {"predictions": gemini_result.get('predictions', []), "source": "gemini"}
        
        # Step 6: If no match and Gemini failed, try Gemini with force
        print("⚠️  Trying Gemini API again with fresh request...")
        gemini_retry = call_gemini_api(user_input)
        if gemini_retry.get('predictions') and len(gemini_retry.get('predictions', [])) > 0:
            print(f"✅ Returning Gemini predictions (retry): {len(gemini_retry.get('predictions', []))} diseases")
            return {"predictions": gemini_retry.get('predictions', []), "source": "gemini"}
        
        # Step 7: Return empty if both fail
        print("❌ No predictions found, returning empty")
        return {"predictions": [], "source": "none"}
    
    except Exception as e:
        import traceback
        print(f"ERROR in predict: {str(e)}")
        print(traceback.format_exc())
        return {"predictions": [], "source": "error", "error": str(e)}

@app.get('/')
def root():
    return {
        'status': 'online',
        'service': 'AI Disease Diagnosis API',
        'version': '1.0',
        'symptoms_recognized': len(symptom_vocab)
    }

if __name__ == '__main__':
    import uvicorn
    print("\n🚀 Starting Python FastAPI server on http://localhost:8000")
    print("📊 AI model ready for predictions")
    uvicorn.run(app, host='0.0.0.0', port=8000)

