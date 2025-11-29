#!/usr/bin/env python
"""Start the FastAPI server."""
import sys
import os

# Add lib to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from predict import app
import uvicorn

if __name__ == '__main__':
    print("\n🚀 Starting Python FastAPI server on http://localhost:8000")
    print("📊 AI model ready for predictions\n")
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
