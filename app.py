from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import calendar
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)

ADMIN_PASSWORD = 'admin'

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Use string for date in 'YYYY-MM-DD' format
    room = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(10), nullable=False)

# Create the database and the Booking table
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    bookings = Booking.query.all()
    return render_template('index.html', bookings=bookings)

@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    date = request.form['date']
    time = request.form['time']
    room = request.form['room']

    # Check if the room is already booked on the selected date
    existing_booking = Booking.query.filter_by(date=date, room=room).first()
    if existing_booking:
        error_message = "This room is already booked on the selected date."
        return redirect(url_for('index', error=error_message))
    
    # Create a new booking
    new_booking = Booking(name=name, date=date, room=room, time=time)
    db.session.add(new_booking)
    db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/calendar', methods=['GET'])
def calendar_view():
    month = int(request.args.get('month', datetime.now().month))
    year = int(request.args.get('year', datetime.now().year))

    # Calculate previous and next month
    prev_month, prev_year = (month - 1, year) if month > 1 else (12, year - 1)
    next_month, next_year = (month + 1, year) if month < 12 else (1, year + 1)

    month_days = calendar.monthcalendar(year, month)

    # Get booked dates for the current month and year
    bookings = Booking.query.all()
    booked_dates = {
        datetime.strptime(booking.date, '%Y-%m-%d').day
        for booking in bookings
        if datetime.strptime(booking.date, '%Y-%m-%d').month == month and datetime.strptime(booking.date, '%Y-%m-%d').year == year
    }

    return render_template('calendar.html', month_days=month_days, booked_dates=booked_dates, year=year, month=month, prev_month=prev_month, prev_year=prev_year, next_month=next_month, next_year=next_year, calendar=calendar)

@app.route('/booking')
def booking():
    return render_template('index.html')  # Create a booking.html template for the booking form

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        date_to_delete = request.form['date']
        
        if password == ADMIN_PASSWORD:
            # Find the booking for the specified date
            booking_to_delete = Booking.query.filter_by(date=date_to_delete).first()
            if booking_to_delete:
                db.session.delete(booking_to_delete)
                db.session.commit()
                return 'Booking deleted successfully.'
            else:
                return 'No booking found for this date.'
        else:
            return 'Incorrect password. Please try again.'

    return render_template('admin.html')

# @app.route('/admin/delete', methods=['POST'])
# def admin_delete():
#     password = request.form['password']
#     date_to_delete = request.form['date']
    
#     if password == ADMIN_PASSWORD:
#         booking_to_delete = Booking.query.filter_by(date=date_to_delete).first()
#         if booking_to_delete:
#             db.session.delete(booking_to_delete)
#             db.session.commit()
#             return 'Booking deleted successfully.'
#         else:
#             return 'No booking found for this date.'
#     else:
#         return 'Incorrect password. Please try again.'

@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    password = request.form['password']
    date_to_delete = request.form['date']
    
    if password == ADMIN_PASSWORD:
        booking_to_delete = Booking.query.filter_by(date=date_to_delete).first()
        if booking_to_delete:
            db.session.delete(booking_to_delete)
            db.session.commit()
            flash('Booking deleted successfully.', 'success')
        else:
            flash('No booking found for this date.', 'error')
    else:
        flash('Incorrect password. Please try again.', 'error')
    
    return redirect(url_for('admin'))
    

if __name__ == '__main__':
    app.run(debug=True)