from flask import Flask, render_template, jsonify
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = "YOUR_ALPHA_VANTAGE_KEY" # <--- Put your key here
SYMBOL = "EURUSD"

def get_fx_data():
    url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=15min&apikey={API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        time_series = data.get("Time Series FX (15min)", {})
        
        # Get Current Price (latest candle)
        latest_time = sorted(time_series.keys())[-1]
        current_price = float(time_series[latest_time]["4. close"])
        
        # Find Session Opens (Logic: look for closest timestamp to 00:00, 08:00, 13:00)
        # For a basic personal tracker, we'll search the last 100 periods
        daily_open = None
        london_open = None
        ny_open = None

        for ts, ohlc in time_series.items():
            time_obj = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            if time_obj.hour == 0 and time_obj.minute == 0: daily_open = float(ohlc["1. open"])
            if time_obj.hour == 8 and time_obj.minute == 0: london_open = float(ohlc["1. open"])
            if time_obj.hour == 13 and time_obj.minute == 0: ny_open = float(ohlc["1. open"])

        return {
            "current": current_price,
            "daily": daily_open or current_price, # Fallback if data point missing
            "london": london_open or current_price,
            "ny": ny_open or current_price
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    data = get_fx_data()
    if not data: return jsonify({"error": "No data"}), 500
    
    curr = data["current"]
    # 10,000 multiplier for standard 4-decimal pips
    pips = lambda op: round((curr - op) * 10000, 1)

    return jsonify({
        "current": curr,
        "daily": {"open": data["daily"], "pips": pips(data["daily"])},
        "london": {"open": data["london"], "pips": pips(data["london"])},
        "ny": {"open": data["ny"], "pips": pips(data["ny"])}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
