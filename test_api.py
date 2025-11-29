#!/usr/bin/env python
import requests
import json
import time

# Wait for server to start
time.sleep(2)

# Test 1: Structured symptoms
print("\n=== Test 1: Structured Symptoms (fever, cough) ===")
try:
    response = requests.post(
        'http://localhost:8000/predict',
        json={'symptoms': 'fever, cough'},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Free-form text
print("\n=== Test 2: Free-Form Text (pain in neck) ===")
try:
    response = requests.post(
        'http://localhost:8000/predict',
        json={'symptoms': 'i have pain in neck'},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Casual text
print("\n=== Test 3: Casual Text (feel nervous and tired) ===")
try:
    response = requests.post(
        'http://localhost:8000/predict',
        json={'symptoms': 'feel nervous and tired'},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Tests completed ===")
