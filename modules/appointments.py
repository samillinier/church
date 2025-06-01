from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Appointment
from datetime import datetime

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointments_bp.route('/')
@login_required
def index():
    appointments = Appointment.query.all()
    return render_template('appointments/index.html', appointments=appointments)

@appointments_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        
        try:
            date_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            appointment = Appointment(
                title=title,
                description=description,
                date_time=date_time,
                user_id=current_user.id
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment created successfully!', 'success')
            return redirect(url_for('appointments.index'))
            
        except Exception as e:
            flash('Error creating appointment. Please try again.', 'error')
            return render_template('create_appointment.html')
    
    return render_template('create_appointment.html') 