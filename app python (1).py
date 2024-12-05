from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests

app = Flask(__name__)

API_URL = "https://open.er-api.com/v6/latest/"  # Using this API URL for currency conversion

# Database setup
def init_db():
    conn = sqlite3.connect('heeniya_voyage.db')
    cursor = conn.cursor()

    # Create bookings table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        dob TEXT,
        mobile TEXT,
        persons INTEGER,
        travel_date TEXT,
        days INTEGER
    )''')

    # Create payments table to store payment details
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cardholder TEXT,
        card_number TEXT,
        expiry TEXT,
        cvv TEXT
    )''')

    conn.commit()
    conn.close()



# Routes
@app.route('/')
def home():
    return render_template('tour_management.html')

@app.route('/book')
def book():
    return render_template('book.html')

@app.route('/payment', methods=['POST'])
def payment():
    # Save booking details in DB
    data = request.form
    conn = sqlite3.connect('heeniya_voyage.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO bookings (name, age, dob, mobile, persons, travel_date, days)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (data['name'], data['age'], data['dob'], data['mobile'], data['persons'], data['date'], data['days']))
    conn.commit()
    conn.close()
    return render_template('payment.html', amount=1500 * int(data['persons']))  # Example calculation

@app.route('/currency-converter', methods=['GET', 'POST'])  # Updated the route to use hyphens
def currency_converter():
    if request.method == 'POST':
        try:
            # Get form data
            amount = float(request.form.get('amount'))
            from_currency = request.form.get('from_currency')
            to_currency = request.form.get('to_currency')

            # Fetch conversion rates
            response = requests.get(f"{API_URL}{from_currency}")
            if response.status_code == 200:
                rates = response.json().get('rates', {})
                if to_currency in rates:
                    converted_amount = amount * rates[to_currency]
                    return render_template(
                        'currency_converter.html',
                        converted_amount=round(converted_amount, 2),
                        from_currency=from_currency,
                        to_currency=to_currency,
                        amount=amount
                    )
                else:
                    error = f"Currency {to_currency} not supported."
            else:
                error = "Failed to fetch conversion rates. Please try again later."

        except ValueError:
            error = "Invalid amount entered. Please enter a numeric value."
        
        # Handle errors and return to the form
        return render_template('currency_converter.html', error=error)

    # Render the converter form initially
    return render_template('currency_converter.html', converted_amount=None)


@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    # Get form data
    cardholder = request.form.get('cardholder')
    card_number = request.form.get('card')
    expiry = request.form.get('expiry')
    cvv = request.form.get('cvv')

    # Store payment details in DB
    conn = sqlite3.connect('heeniya_voyage.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO payments (cardholder, card_number, expiry, cvv)
                      VALUES (?, ?, ?, ?)''',
                   (cardholder, card_number, expiry, cvv))
    conn.commit()
    conn.close()

    return render_template('tour_management.html')



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
