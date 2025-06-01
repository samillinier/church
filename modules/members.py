from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User
from datetime import datetime

members_bp = Blueprint('members', __name__, url_prefix='/members')

@members_bp.route('/')
@login_required
def index():
    members = User.query.filter_by(_is_active=True).all()
    return render_template('members/index.html', members=members)

@members_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    member = User.query.get_or_404(user_id)
    return render_template('profile.html', member=member)

@members_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    member = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            member.first_name = request.form.get('first_name')
            member.last_name = request.form.get('last_name')
            member.email = request.form.get('email')
            member.phone = request.form.get('phone')
            member.address = request.form.get('address')
            member.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d')
            member.gender = request.form.get('gender')
            member.marital_status = request.form.get('marital_status')
            member.occupation = request.form.get('occupation')
            member.ministry = request.form.get('ministry')
            member.membership_status = request.form.get('membership_status')
            member.baptism_status = request.form.get('baptism_status') == 'true'
            
            if request.form.get('baptism_date'):
                member.baptism_date = datetime.strptime(request.form.get('baptism_date'), '%Y-%m-%d')
            
            db.session.commit()
            flash('Member information updated successfully!', 'success')
            return redirect(url_for('members.profile', user_id=user_id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating member information. Please try again.', 'error')
    
    return render_template('edit_member.html', member=member) 