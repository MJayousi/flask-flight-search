import re
import requests
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

# Amadeus API credentials
API_KEY = "9Fh8uxoiOWyopw2n9FCm0Mh56xooAv9W"
API_SECRET = "ZHSQOcT6Osj4ZrgL"
TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
SEARCH_URL = "https://test.api.amadeus.com/v1/shopping/flight-destinations"

def get_access_token():
    """Retrieve an access token from Amadeus API."""
    response = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": API_SECRET
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Error retrieving access token:", response.json())
        return None

def validate_iata_code(code):
    """Validate if the input is a 3-letter IATA airport code."""
    return bool(re.fullmatch(r"[A-Z]{3}", code))

def validate_date(date_str):
    """Validate if the input is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def get_flights(departure, date, budget, token):
    """Fetch direct flights from Amadeus API."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "origin": departure,
        "departureDate": date,
        "maxPrice": budget,
        "nonStop": "true"
    }
    response = requests.get(SEARCH_URL, headers=headers, params=params)

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"API Error {response.status_code}: {response.text}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    flights = []
    error = None
    if request.method == 'POST':
        departure = request.form.get('departure').strip().upper()
        date = request.form.get('date').strip()
        budget = request.form.get('budget').strip()
        
        if not validate_iata_code(departure):
            error = "Invalid IATA code. Please enter a valid 3-letter airport code."
        elif not validate_date(date):
            error = "Invalid date format. Please enter in YYYY-MM-DD format."
        elif not budget.isdigit() or int(budget) <= 0:
            error = "Invalid budget. Please enter a positive number."
        else:
            token = get_access_token()
            if token:
                flights = get_flights(departure, date, int(budget), token)
            else:
                error = "Error retrieving access token. Please try again later."
    
    return render_template('index.html', flights=flights, error=error)

if __name__ == "__main__":
    app.run(debug=True)
