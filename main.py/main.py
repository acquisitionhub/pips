from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Mock Data - Replace with your Forex API (e.g., OANDA or AlphaVantage)
def get_market_data():
    return {
        "current_price": 1.0850,
        "daily_open": 1.0820,
        "london_open": 1.0840,
        "ny_open": 1.0860
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tracker')
def tracker():
    data = get_market_data()
    curr = data["current_price"]
    
    # Calculate Pips (assuming 4-decimal pair like EUR/USD)
    stats = {
        "daily": {"open": data["daily_open"], "dist": round((curr - data["daily_open"]) * 10000, 1)},
        "london": {"open": data["london_open"], "dist": round((curr - data["london_open"]) * 10000, 1)},
        "ny": {"open": data["ny_open"], "dist": round((curr - data["ny_open"]) * 10000, 1)},
        "current": curr
    }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
