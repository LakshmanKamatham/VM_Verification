#!/usr/bin/env python3
"""
Alternative launcher for Bootcode Verification Chatbot
Runs on port 8080 to avoid conflicts
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app

if __name__ == '__main__':
    print("🚀 Starting Bootcode Verification Chatbot on alternative port...")
    print("📍 Access the chatbot at: http://localhost:8080")
    print("🔧 This runs on port 8080 to avoid conflicts with port 5000")
    print("=" * 60)
    
    # Run on alternative port
    app.run(debug=True, host='0.0.0.0', port=8080)