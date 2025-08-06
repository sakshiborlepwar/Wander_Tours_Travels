import os

if os.path.exists("travels.db"):
    os.remove("travels.db")

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(200))
    price = db.Column(db.Integer)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    contact = db.Column(db.String(20))
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'))
    destination = db.relationship('Destination')
    date = db.Column(db.String(50))

@app.route('/')
def home():
    destinations = Destination.query.all()
    return render_template('home.html', destinations=destinations)

@app.route('/book/<int:destination_id>')
def book(destination_id):
    destination = Destination.query.get(destination_id)
    return render_template('booking.html', destination=destination)

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    name = request.form['name']
    email = request.form['email']
    contact = request.form['contact']
    destination_id = request.form['destination_id']
    travel_date = request.form['travelDateGoa']
    destination = Destination.query.get(destination_id)

    booking = Booking(name=name, email=email, contact=contact, destination=destination, date=travel_date)
    db.session.add(booking)
    db.session.commit()

    flash('Booking confirmed successfully!')
    return redirect(url_for('home'))

@app.route('/bookings')
def bookings():
    all_bookings = Booking.query.all()
    return render_template('bookings.html', bookings=all_bookings)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Destination.query.first():
            db.session.add_all([
                Destination(name='Goa Delight', description='Sunny beaches and fun!', price=10000),
                Destination(name='Manali Adventure', description='Himalayan beauty and adventure', price=18000),
                Destination(name='Paris', description='City of lights with iconic art',price=120000),
                Destination(name='Bali Bliss', description='Beaches and temples',price=100000)

            ])
            db.session.commit()
    app.run(debug=True)
