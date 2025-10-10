import os

if os.path.exists("travels.db"):
    os.remove("travels.db")

from flask import Flask, render_template, request, redirect, url_for, flash,session
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

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    message = db.Column(db.String(500))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'))
    destination = db.relationship('Destination')
    review_text = db.Column(db.String(500))
    rating = db.Column(db.Integer)
    emoji = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def home():
    destinations = Destination.query.all()
    return render_template('home.html', destination=destinations)

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

# View all contact enquiries
@app.route('/contacts')
def view_contacts():
    all_contacts = Contact.query.order_by(Contact.id.asc()).all()
    return render_template('contacts.html', contacts=all_contacts)

# View all feedbacks
@app.route('/feedbacks')
def view_feedbacks():
    all_feedbacks = Feedback.query.order_by(Feedback.id.asc()).all()
    return render_template('feedbacks.html', feedbacks=all_feedbacks)


# ======= CONTACT FORM =======

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    if not name or not email or not message:
        flash("Please fill all contact fields.", "error")
        return redirect(url_for('home'))

    contact_entry = Contact(name=name, email=email, message=message)
    db.session.add(contact_entry)
    db.session.commit()
    flash("📩 Thank you! Your enquiry has been submitted.")
    return redirect(url_for('home'))

# ======= FEEDBACK FORM =======

@app.route('/feedback', methods=['POST'])
def feedback():
    name = request.form['feedbackName']
    email = request.form['feedbackEmail']
    message = request.form['feedbackMessage']

    if not name or not email or not message:
        flash("Please fill all feedback fields.", "error")
        return redirect(url_for('home'))

    feedback_entry = Feedback(name=name, email=email, message=message)
    db.session.add(feedback_entry)
    db.session.commit()
    flash("✅ Feedback submitted successfully!")
    return redirect(url_for('home'))

# ===================== ADMIN LOGIN =====================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hardcoded admin credentials
        if username == 'admin' and password == 'Admin@123':  # <-- Change this as needed
            session['admin_logged_in'] = True
            flash("✅ Admin login successful!")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("❌ Invalid username or password.", "error")
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully!")
    return redirect(url_for('home'))


@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    all_bookings = Booking.query.order_by(Booking.id.asc()).all()
    all_contacts = Contact.query.order_by(Contact.id.asc()).all()
    all_feedbacks = Feedback.query.order_by(Feedback.id.asc()).all()

    return render_template(
        'admin_dashboard.html',
        bookings=all_bookings,
        contacts=all_contacts,
        feedbacks=all_feedbacks
    )

# ======= INITIALIZE DATABASE =======

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
 