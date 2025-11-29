import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import joblib
import json
import os

print("Training AI disease prediction model with Kaggle dataset...")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, 'archive', 'dataset.csv')

print(f"Loading dataset from: {csv_path}")
df = pd.read_csv(csv_path, nrows=10000)

print(f"Loaded {len(df)} records (sampled from 246K+)")
print(f"Columns: {len(df.columns)} (1 disease + {len(df.columns)-1} symptoms)")

symptom_cols = [col for col in df.columns if col != 'diseases']
print(f"Unique symptoms: {len(symptom_cols)}")


                                                        
diseaseMap = {}
print("Processing diseases and symptoms...")
for idx, row in df.iterrows():
    disease = row['diseases']
    if disease not in diseaseMap:
        diseaseMap[disease] = np.zeros(len(symptom_cols))
    
    for i, symptom in enumerate(symptom_cols):
        if row[symptom] == 1:
            diseaseMap[disease][i] = 1
    
    if idx % 1000 == 0:
        print(f"Processed {idx}/{len(df)} records...")

diseases = list(diseaseMap.keys())
X = np.array([diseaseMap[d] for d in diseases])
y = np.array(diseases)

print(f"Unique diseases: {len(diseases)}")

if len(diseases) > 1:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LogisticRegression(max_iter=500, solver='lbfgs')
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy*100:.2f}%")
else:
    model = LogisticRegression(max_iter=500, solver='lbfgs')
    model.fit(X, y)
    print("Training on full dataset (too few samples for split)")

symptom_vocab = [s.lower().replace('_', ' ') for s in symptom_cols]
print(f"Total symptoms in vocabulary: {len(symptom_vocab)}")

model_data = {
    'model': model,
    'symptom_cols': symptom_cols,
    'symptom_vocab': symptom_vocab,
    'diseases': diseases
}

model_path = os.path.join(base_dir, 'lib', 'disease_model.pkl')
joblib.dump(model_data, model_path)
print(f"Model saved successfully to {model_path}")

knowledge_path = os.path.join(base_dir, 'data', 'knowledge-base.json')
with open(knowledge_path, 'r') as f:
    knowledge = json.load(f)

print("\nModel training complete!")
print(f"- Diseases trained: {len(set(diseases))}")
print(f"- Symptoms recognized: {len(symptom_vocab)}")
print("- Ready for predictions")

