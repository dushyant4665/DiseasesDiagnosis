#!/usr/bin/env python
"""Launch script for the FastAPI server with proper module path."""
import sys
import os

# Add lib directory to Python path so imports work
lib_dir = os.path.join(os.path.dirname(__file__))
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

# Now import and run
if __name__ == '__main__':
    from predict import app
    import uvicorn
    
    config = uvicorn.Config(
        app=app,
        host='0.0.0.0',
        port=8000,
        log_level='info',
    )
    server = uvicorn.Server(config)
    server.run()
