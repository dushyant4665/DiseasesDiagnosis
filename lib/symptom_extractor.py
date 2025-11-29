"""
NLP Symptom Extraction using Google Gemini API.
Converts natural language input (e.g., "I have pain in my neck") to symptom tokens.
"""

import os
import json
import re
from typing import List, Optional

# Try to import Gemini, fallback to regex-based extraction if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Google Generative AI not installed. Using regex-based extraction.")

# Symptom keywords for fallback regex-based matching
SYMPTOM_KEYWORDS = {
    'fever': ['fever', 'high temperature', 'temp', 'burning'],
    'cough': ['cough', 'coughing', 'coughs'],
    'headache': ['headache', 'head pain', 'migraine', 'head ache'],
    'body_pain': ['body pain', 'body ache', 'aches', 'pain', 'soreness'],
    'fatigue': ['fatigue', 'tired', 'exhausted', 'tiredness', 'weakness'],
    'sore_throat': ['sore throat', 'throat pain', 'throat ache'],
    'chills': ['chills', 'shivering', 'chilly'],
    'shortness_of_breath': ['shortness of breath', 'breathlessness', 'difficulty breathing', 'can\'t breathe'],
    'diarrhea': ['diarrhea', 'loose stools', 'loose motion', 'diarrhoea'],
    'nausea': ['nausea', 'feeling sick', 'queasy', 'sick feeling'],
    'vomiting': ['vomiting', 'throwing up', 'vomit'],
    'runny_nose': ['runny nose', 'nasal discharge', 'nose running'],
    'congestion': ['congestion', 'nasal congestion', 'stuffy nose', 'blocked nose'],
    'muscle_pain': ['muscle pain', 'muscle ache', 'myalgia'],
    'joint_pain': ['joint pain', 'joint ache', 'arthralgia'],
    'rash': ['rash', 'skin rash', 'eruption'],
    'itching': ['itching', 'itchy', 'itches'],
    'difficulty_breathing': ['difficulty breathing', 'hard to breathe', 'breathing difficulty'],
    'chest_pain': ['chest pain', 'chest ache', 'pain in chest'],
    'anxiety': ['anxiety', 'anxious', 'nervous', 'feel nervous', 'worry', 'worried', 'worried'],
    'dizziness': ['dizziness', 'dizzy', 'vertigo', 'lightheaded'],
    'weakness': ['weakness', 'weak', 'feeble'],
    'loss_of_appetite': ['loss of appetite', 'no appetite', 'don\'t want to eat'],
    'abdominal_pain': ['abdominal pain', 'belly pain', 'stomach pain', 'stomach ache', 'pain in stomach'],
    'constipation': ['constipation', 'constipated'],
    'indigestion': ['indigestion', 'dyspepsia'],
    'sweating': ['sweating', 'sweat', 'sweaty'],
    'stiff_neck': ['stiff neck', 'neck stiffness', 'neck pain', 'pain in neck', 'neck ache'],
}

class SymptomExtractor:
    def __init__(self, api_key: Optional[str] = None, use_gemini: bool = True):
        """
        Initialize symptom extractor.
        
        Args:
            api_key: Google Gemini API key (can be set via GEMINI_API_KEY env var)
            use_gemini: Whether to use Gemini API (falls back to regex if False or API unavailable)
        """
        self.use_gemini = use_gemini and GEMINI_AVAILABLE
        
        if self.use_gemini:
            api_key = api_key or os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini API initialized successfully")
            else:
                print("⚠️ GEMINI_API_KEY not found. Falling back to regex extraction.")
                self.use_gemini = False
    
    def extract_symptoms_gemini(self, user_input: str) -> List[str]:
        """
        Use Gemini API to extract symptoms from natural language.
        
        Args:
            user_input: Natural language input (e.g., "I have pain in my neck")
        
        Returns:
            List of extracted symptom tokens
        """
        try:
            prompt = f"""You are a medical assistant. Extract medical symptoms from the user's input.
            
User input: "{user_input}"

Return ONLY a JSON array of symptom tokens in lowercase with underscores (no spaces).
Choose from these common symptoms: {list(SYMPTOM_KEYWORDS.keys())}

Example:
Input: "I have fever and a bad cough"
Output: ["fever", "cough"]

Input: "My neck hurts and I feel anxious"
Output: ["stiff_neck", "anxiety"]

Now extract symptoms from the input above. Return only the JSON array, nothing else."""

            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse JSON response
            try:
                symptoms = json.loads(text)
                if isinstance(symptoms, list):
                    # Validate symptoms are in our vocabulary
                    valid_symptoms = [s for s in symptoms if s in SYMPTOM_KEYWORDS]
                    print(f"🔍 Gemini extracted: {valid_symptoms}")
                    return valid_symptoms
            except json.JSONDecodeError:
                print(f"⚠️ Could not parse Gemini response: {text[:100]}")
        except Exception as e:
            print(f"⚠️ Gemini API error: {e}. Falling back to regex.")
        
        # Fallback to regex
        return self.extract_symptoms_regex(user_input)
    
    def extract_symptoms_regex(self, user_input: str) -> List[str]:
        """
        Fallback: Use regex-based pattern matching to extract symptoms.
        
        Args:
            user_input: Natural language input
        
        Returns:
            List of extracted symptom tokens
        """
        user_input_lower = user_input.lower()
        found_symptoms = set()
        
        for symptom_token, keywords in SYMPTOM_KEYWORDS.items():
            for keyword in keywords:
                if keyword in user_input_lower:
                    found_symptoms.add(symptom_token)
                    break
        
        result = list(found_symptoms)
        print(f"🔍 Regex extracted: {result}")
        return result
    
    def extract_symptoms(self, user_input: str) -> List[str]:
        """
        Extract symptoms from user input using Gemini or regex fallback.
        
        Args:
            user_input: Natural language symptom description
        
        Returns:
            List of symptom tokens understood by the ML model
        """
        if not user_input or not user_input.strip():
            return []
        
        if self.use_gemini:
            return self.extract_symptoms_gemini(user_input)
        else:
            return self.extract_symptoms_regex(user_input)


# Global extractor instance
_extractor = None

def get_symptom_extractor(api_key: Optional[str] = None) -> SymptomExtractor:
    """Get or create the global symptom extractor."""
    global _extractor
    if _extractor is None:
        _extractor = SymptomExtractor(api_key=api_key)
    return _extractor


def extract_symptoms(user_input: str) -> List[str]:
    """Convenience function to extract symptoms."""
    extractor = get_symptom_extractor()
    return extractor.extract_symptoms(user_input)


if __name__ == '__main__':
    # Test the extractor
    test_inputs = [
        "I have fever and cough",
        "I have pain in my neck and feel nervous",
        "I have chest pain and difficulty breathing",
        "My stomach hurts and I feel dizzy",
    ]
    
    extractor = SymptomExtractor()
    
    print("\n🧪 Testing Symptom Extractor\n")
    for test_input in test_inputs:
        print(f"Input: {test_input}")
        symptoms = extractor.extract_symptoms(test_input)
        print(f"Output: {symptoms}\n")
