import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer
import joblib
import numpy as np
import os

print("Training AI Disease Diagnosis Model...")
print("=" * 50)

# Load dataset
dataset_path = '../archive/dataset.csv'
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"Dataset not found at {dataset_path}")

df = pd.read_csv(dataset_path)
print(f'✅ Loaded {len(df)} records')

# Identify symptom columns and disease column
symptom_cols = [col for col in df.columns if col != 'diseases']
disease_col = 'diseases'

print(f'✅ Found {len(symptom_cols)} symptom features')
print(f'✅ Found {len(df[disease_col].unique())} unique diseases')

# Create symptom vocabulary
symptom_vocab = set()
for col in symptom_cols:
    symptom_vocab.add(col.lower().replace('_', ' '))
    symptom_vocab.add(col.lower())

# Prepare features and labels
X = df[symptom_cols].values
y = df[disease_col].values

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("\nTraining model...")
print("-" * 50)

# Train model
model = LogisticRegression(max_iter=1000, multi_class='multinomial', solver='lbfgs', random_state=42)
model.fit(X_train, y_train)

# Evaluate model
train_accuracy = model.score(X_train, y_train)
test_accuracy = model.score(X_test, y_test)

print(f'✅ Training accuracy: {train_accuracy:.2%}')
print(f'✅ Test accuracy: {test_accuracy:.2%}')

# Prepare model data
model_data = {
    'model': model,
    'symptom_cols': symptom_cols,
    'symptom_vocab': list(symptom_vocab),
    'classes': model.classes_.tolist()
}

# Save to multiple locations for compatibility
print("\nSaving model...")
print("-" * 50)

# Save to model directory
joblib.dump(model_data, 'model.joblib')
print('✅ Model saved to model/model.joblib')

# Save to lib directory
lib_path = '../lib/disease_model.pkl'
os.makedirs(os.path.dirname(lib_path), exist_ok=True)
joblib.dump(model_data, lib_path)
print(f'✅ Model saved to {lib_path}')

print("\n" + "=" * 50)
print("Model training completed successfully!")
print("=" * 50)


