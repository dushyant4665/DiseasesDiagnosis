from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import json
import os
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading AI model...")
# Load model from current directory
if os.path.exists('model.joblib'):
    model_data = joblib.load('model.joblib')
else:
    # Fallback to parent lib directory
    model_data = joblib.load('../lib/disease_model.pkl')

model = model_data['model']
symptom_cols = model_data['symptom_cols']
classes = model.classes_

# Create symptom vocabulary
symptom_vocab = set()
for col in symptom_cols:
    symptom_vocab.add(col.lower().replace('_', ' '))
    symptom_vocab.add(col.lower())

# Load knowledge base
knowledge_path = '../data/knowledge-base.json'
if os.path.exists(knowledge_path):
    with open(knowledge_path, 'r') as f:
        knowledge = json.load(f)
else:
    knowledge = {'recommendations': {'default': 'Consult a healthcare professional for proper diagnosis and treatment.'}}

print(f"✅ AI model loaded successfully")
print(f"✅ Recognizes {len(symptom_vocab)} symptoms")

class PredictRequest(BaseModel):
    symptoms: str

class PredictionItem(BaseModel):
    disease: str
    confidence: float
    matched_symptoms: List[str]
    recommendation: str

class PredictResponse(BaseModel):
    predictions: List[PredictionItem]

@app.post('/predict', response_model=PredictResponse)
def predict(req: PredictRequest):
    input_symptoms = [s.strip().lower() for s in req.symptoms.split(',') if s.strip()]
    
    if not input_symptoms:
        return PredictResponse(predictions=[])
    
    # Match symptoms to vocabulary
    matched_symptoms = []
    input_vector = np.zeros(len(symptom_cols))
    
    for symptom in input_symptoms:
        symptom_normalized = symptom.replace(' ', '_')
        # Try direct match
        if symptom_normalized in symptom_cols:
            idx = symptom_cols.index(symptom_normalized)
            input_vector[idx] = 1
            matched_symptoms.append(symptom)
        else:
            # Try with spaces replaced by underscores
            for i, col in enumerate(symptom_cols):
                col_normalized = col.lower().replace('_', ' ')
                if col_normalized == symptom or col.lower() == symptom:
                    input_vector[i] = 1
                    matched_symptoms.append(symptom)
                    break
    
    if input_vector.sum() == 0:
        return PredictResponse(predictions=[])
    
    input_vector = input_vector.reshape(1, -1)
    probs = model.predict_proba(input_vector)[0]
    
    top_indices = np.argsort(probs)[-5:][::-1]
    
    predictions = []
    for idx in top_indices:
        if probs[idx] > 0.01:
            disease = classes[idx]
            confidence = round(float(probs[idx]), 2)
            
            # Get recommendation from knowledge base
            recommendation = knowledge['recommendations'].get(
                disease,
                knowledge['recommendations'].get('default', 'Consult a healthcare professional.')
            )
            
            predictions.append(PredictionItem(
                disease=disease,
                confidence=confidence,
                matched_symptoms=matched_symptoms,
                recommendation=recommendation
            ))
    
    return PredictResponse(predictions=predictions)

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