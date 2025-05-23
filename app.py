from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from sqlalchemy import or_
import os
from werkzeug.utils import secure_filename
import json
import calendar

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///church.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Cell Team Membership Association Table
cell_team_members = db.Table('cell_team_members',
    db.Column('cell_team_id', db.Integer, db.ForeignKey('cell_team.id'), primary_key=True),
    db.Column('member_id', db.Integer, db.ForeignKey('member.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class CellTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    meeting_day = db.Column(db.String(20))
    meeting_time = db.Column(db.String(20))
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    leader = db.relationship('Member', foreign_keys=[leader_id])
    members = db.relationship('Member', secondary=cell_team_members, 
                            backref=db.backref('cell_teams', lazy='dynamic'))

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    photo = db.Column(db.String(500))  # Path to stored photo
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    marital_status = db.Column(db.String(20))
    occupation = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    membership_status = db.Column(db.String(50), default='Active')
    baptism_status = db.Column(db.Boolean, default=False)
    baptism_date = db.Column(db.Date)
    previous_church = db.Column(db.String(200))
    ministry = db.Column(db.String(100))
    spiritual_gifts = db.Column(db.String(200))
    leadership_roles = db.Column(db.String(200))
    family_members = db.Column(db.String(500))
    skills_talents = db.Column(db.String(500))
    prayer_requests = db.Column(db.Text)
    notes = db.Column(db.Text)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # letter, report, announcement, etc.
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(500))  # For attached files
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, archived, deleted
    tags = db.Column(db.String(200))  # Comma-separated tags for easy searching
    related_members = db.Column(db.String(500))  # Comma-separated member IDs

class Marriage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Member relationships
    bride_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    groom_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    bride = db.relationship('Member', foreign_keys=[bride_id])
    groom = db.relationship('Member', foreign_keys=[groom_id])
    
    # Wedding Details
    wedding_date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(200))
    service_type = db.Column(db.String(50))  # Traditional, Church Wedding, etc.
    
    # Course Information
    required_courses = db.Column(db.Text)  # JSON list of required courses
    completed_courses = db.Column(db.Text)  # JSON list of completed courses
    next_course_date = db.Column(db.Date)
    course_notes = db.Column(db.Text)
    
    # Waiting Period
    application_date = db.Column(db.Date, default=datetime.utcnow)
    waiting_period_end = db.Column(db.Date)  # Calculated field
    waiting_period_status = db.Column(db.String(50))  # In Progress, Completed, Waived
    waiver_reason = db.Column(db.Text)
    
    # Counseling Information
    counseling_status = db.Column(db.String(50))  # Pending, Completed, Not Started
    counseling_notes = db.Column(db.Text)
    next_counseling_date = db.Column(db.Date)
    counseling_sessions_completed = db.Column(db.Integer, default=0)
    
    # Documentation
    documents_submitted = db.Column(db.Boolean, default=False)
    document_notes = db.Column(db.Text)
    
    # Additional Information
    parents_approval = db.Column(db.Boolean, default=False)
    officiating_minister = db.Column(db.String(100))
    witnesses = db.Column(db.Text)
    special_requirements = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pending')  # Pending, Approved, Completed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))  # 'birthday', 'anniversary'
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    date = db.Column(db.Date)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reference_id = db.Column(db.Integer)  # ID of the related member or marriage

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    counselor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    appointment_type = db.Column(db.String(50))  # Marriage, Personal, Family, etc.
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)  # Format: "HH:MM"
    duration = db.Column(db.Integer, default=60)  # Duration in minutes
    status = db.Column(db.String(20), default='Pending')  # Pending, Confirmed, Completed, Cancelled
    notes = db.Column(db.Text)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    member = db.relationship('Member', backref='appointments')
    counselor = db.relationship('User', backref='counseling_appointments')

class FinanceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('FinanceTransaction', backref='category', lazy=True)

class FinanceTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('finance_category.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    payment_method = db.Column(db.String(50))  # cash, check, bank transfer, etc.
    reference_number = db.Column(db.String(100))  # check number, transfer reference, etc.
    description = db.Column(db.Text)
    transaction_date = db.Column(db.Date, nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='completed')  # pending, completed, cancelled
    notes = db.Column(db.Text)
    
    # For offerings/tithes
    service_type = db.Column(db.String(50))  # Sunday Service, Midweek, Special Event, etc.
    envelope_number = db.Column(db.String(50))
    donor_name = db.Column(db.String(200))
    is_anonymous = db.Column(db.Boolean, default=False)
    
    # For expenses
    vendor_name = db.Column(db.String(200))
    receipt_number = db.Column(db.String(100))
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approval_date = db.Column(db.DateTime)
    
    # Relationships
    recorder = db.relationship('User', foreign_keys=[recorded_by], backref='recorded_transactions')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_transactions')

class FinancialReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # daily, weekly, monthly, annual
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_income = db.Column(db.Float, default=0)
    total_expense = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)
    generated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, final, archived
    report_data = db.Column(db.Text)  # JSON string containing detailed report data

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('finance_category.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer)  # Null for annual budgets
    amount = db.Column(db.Float, nullable=False)
    actual_amount = db.Column(db.Float, default=0)
    variance = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, closed
    
    # Relationships
    category = db.relationship('FinanceCategory', backref='budgets')
    creator = db.relationship('User', backref='created_budgets')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle photo upload
        photo_path = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                filename = secure_filename(photo.filename)
                # Create uploads/member_photos directory if it doesn't exist
                photos_dir = os.path.join(app.root_path, 'static', 'uploads', 'member_photos')
                if not os.path.exists(photos_dir):
                    os.makedirs(photos_dir)
                # Save the photo
                photo_path = os.path.join('uploads', 'member_photos', filename)
                photo.save(os.path.join(app.root_path, 'static', photo_path))

        # Get basic information
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Get personal information
        date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None
        gender = request.form.get('gender')
        marital_status = request.form.get('marital_status')
        occupation = request.form.get('occupation')
        
        # Get contact information
        emergency_contact_name = request.form.get('emergency_contact_name')
        emergency_contact_phone = request.form.get('emergency_contact_phone')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        postal_code = request.form.get('postal_code')
        
        # Get church-related information
        membership_status = request.form.get('membership_status')
        baptism_status = request.form.get('baptism_status') == 'yes'
        baptism_date = datetime.strptime(request.form.get('baptism_date'), '%Y-%m-%d').date() if request.form.get('baptism_date') else None
        previous_church = request.form.get('previous_church')
        ministry = request.form.get('ministry')
        spiritual_gifts = request.form.get('spiritual_gifts')
        leadership_roles = request.form.get('leadership_roles')
        family_members = request.form.get('family_members')
        skills_talents = request.form.get('skills_talents')
        prayer_requests = request.form.get('prayer_requests')
        notes = request.form.get('notes')
        
        new_member = Member(
            first_name=first_name,
            last_name=last_name,
            photo=photo_path,
            date_of_birth=date_of_birth,
            gender=gender,
            marital_status=marital_status,
            occupation=occupation,
            email=email,
            phone=phone,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_phone=emergency_contact_phone,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            membership_status=membership_status,
            baptism_status=baptism_status,
            baptism_date=baptism_date,
            previous_church=previous_church,
            ministry=ministry,
            spiritual_gifts=spiritual_gifts,
            leadership_roles=leadership_roles,
            family_members=family_members,
            skills_talents=skills_talents,
            prayer_requests=prayer_requests,
            notes=notes
        )
        
        try:
            db.session.add(new_member)
            db.session.commit()
            flash('Member registered successfully!')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error registering member: ' + str(e))
            
    return render_template('register.html')

@app.route('/member/edit/<int:member_id>', methods=['GET', 'POST'])
@login_required
def edit_member(member_id):
    member = Member.query.get_or_404(member_id)
    
    if request.method == 'POST':
        # Handle photo upload
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                # Delete old photo if it exists
                if member.photo:
                    old_photo_path = os.path.join(app.root_path, 'static', member.photo)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                
                filename = secure_filename(photo.filename)
                photos_dir = os.path.join(app.root_path, 'static', 'uploads', 'member_photos')
                if not os.path.exists(photos_dir):
                    os.makedirs(photos_dir)
                photo_path = os.path.join('uploads', 'member_photos', filename)
                photo.save(os.path.join(app.root_path, 'static', photo_path))
                member.photo = photo_path

        # Update member information
        member.first_name = request.form.get('first_name')
        member.last_name = request.form.get('last_name')
        member.email = request.form.get('email')
        member.phone = request.form.get('phone')
        member.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None
        member.gender = request.form.get('gender')
        member.marital_status = request.form.get('marital_status')
        member.occupation = request.form.get('occupation')
        member.emergency_contact_name = request.form.get('emergency_contact_name')
        member.emergency_contact_phone = request.form.get('emergency_contact_phone')
        member.address = request.form.get('address')
        member.city = request.form.get('city')
        member.state = request.form.get('state')
        member.postal_code = request.form.get('postal_code')
        member.membership_status = request.form.get('membership_status')
        member.baptism_status = request.form.get('baptism_status') == 'yes'
        member.baptism_date = datetime.strptime(request.form.get('baptism_date'), '%Y-%m-%d').date() if request.form.get('baptism_date') else None
        member.previous_church = request.form.get('previous_church')
        member.ministry = request.form.get('ministry')
        member.spiritual_gifts = request.form.get('spiritual_gifts')
        member.leadership_roles = request.form.get('leadership_roles')
        member.family_members = request.form.get('family_members')
        member.skills_talents = request.form.get('skills_talents')
        member.prayer_requests = request.form.get('prayer_requests')
        member.notes = request.form.get('notes')

        try:
            db.session.commit()
            flash('Member updated successfully!')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating member: ' + str(e))

    return render_template('edit_member.html', member=member)

@app.route('/member/delete/<int:member_id>', methods=['POST'])
@login_required
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    
    try:
        # Delete member's photo if it exists
        if member.photo:
            photo_path = os.path.join(app.root_path, 'static', member.photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        
        db.session.delete(member)
        db.session.commit()
        flash('Member deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting member: ' + str(e))
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    search_query = request.args.get('search', '').strip()
    if search_query:
        search = f"%{search_query}%"
        members = Member.query.filter(
            or_(
                Member.first_name.ilike(search),
                Member.last_name.ilike(search),
                Member.email.ilike(search),
                Member.phone.ilike(search),
                Member.ministry.ilike(search),
                Member.membership_status.ilike(search)
            )
        ).all()
    else:
        members = Member.query.all()
    return render_template('dashboard.html', members=members, search_query=search_query)

@app.route('/member-analytics')
@login_required
def member_analytics():
    # Get total members
    total_members = Member.query.count()
    
    # Get membership status distribution
    status_counts = db.session.query(
        Member.membership_status,
        db.func.count(Member.id)
    ).group_by(Member.membership_status).all()
    
    # Get ministry distribution
    ministry_counts = db.session.query(
        Member.ministry,
        db.func.count(Member.id)
    ).group_by(Member.ministry).all()
    
    # Get gender distribution
    gender_counts = db.session.query(
        Member.gender,
        db.func.count(Member.id)
    ).group_by(Member.gender).all()
    
    # Get age group distribution
    current_year = datetime.utcnow().year
    age_groups = {
        '0-12': 0,
        '13-18': 0,
        '19-30': 0,
        '31-50': 0,
        '51+': 0
    }
    
    members = Member.query.filter(Member.date_of_birth != None).all()
    for member in members:
        age = current_year - member.date_of_birth.year
        if age <= 12:
            age_groups['0-12'] += 1
        elif age <= 18:
            age_groups['13-18'] += 1
        elif age <= 30:
            age_groups['19-30'] += 1
        elif age <= 50:
            age_groups['31-50'] += 1
        else:
            age_groups['51+'] += 1
    
    # Get baptism statistics
    baptism_stats = {
        'baptized': Member.query.filter_by(baptism_status=True).count(),
        'not_baptized': Member.query.filter_by(baptism_status=False).count()
    }
    
    # Get monthly member growth (last 12 months)
    current_date = datetime.utcnow()
    last_year = current_date - timedelta(days=365)
    monthly_growth = db.session.query(
        db.func.strftime('%Y-%m', Member.date_joined).label('month'),
        db.func.count(Member.id)
    ).filter(Member.date_joined >= last_year).group_by('month').all()
    
    # Get marital status distribution
    marital_status_counts = db.session.query(
        Member.marital_status,
        db.func.count(Member.id)
    ).group_by(Member.marital_status).all()
    
    return render_template('member_analytics.html',
                         total_members=total_members,
                         status_counts=status_counts,
                         ministry_counts=ministry_counts,
                         gender_counts=gender_counts,
                         age_groups=age_groups,
                         baptism_stats=baptism_stats,
                         monthly_growth=monthly_growth,
                         marital_status_counts=marital_status_counts)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/cell-teams')
@login_required
def cell_teams():
    teams = CellTeam.query.all()
    members = Member.query.all()
    return render_template('cell_teams.html', teams=teams, members=members)

@app.route('/cell-teams/create', methods=['GET', 'POST'])
@login_required
def create_cell_team():
    if request.method == 'POST':
        name = request.form.get('name')
        meeting_day = request.form.get('meeting_day')
        meeting_time = request.form.get('meeting_time')
        location = request.form.get('location')
        description = request.form.get('description')
        member_ids = request.form.getlist('team_members')
        
        # Create a new member for the leader
        leader = Member(
            first_name=request.form.get('leader_first_name'),
            last_name=request.form.get('leader_last_name'),
            email=request.form.get('leader_email'),
            phone=request.form.get('leader_phone'),
            date_joined=datetime.utcnow(),
            membership_status='Active'
        )
        
        try:
            # Add and commit the leader first to get their ID
            db.session.add(leader)
            db.session.commit()
            
            # Create the cell team with the new leader
            team = CellTeam(
                name=name,
                leader_id=leader.id,
                meeting_day=meeting_day,
                meeting_time=meeting_time,
                location=location,
                description=description
            )
            
            db.session.add(team)
            
            # Add selected members to the team
            if member_ids:
                members = Member.query.filter(Member.id.in_(member_ids)).all()
                team.members.extend(members)
            
            # Add the leader as a team member as well
            team.members.append(leader)
            
            db.session.commit()
            flash('Cell team created successfully!')
            return redirect(url_for('cell_teams'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating cell team: ' + str(e))
    
    members = Member.query.all()
    return render_template('create_cell_team.html', members=members)

@app.route('/cell-teams/<int:team_id>')
@login_required
def cell_team_details(team_id):
    team = CellTeam.query.get_or_404(team_id)
    available_members = Member.query.filter(~Member.cell_teams.any(CellTeam.id == team_id)).all()
    return render_template('cell_team_details.html', team=team, available_members=available_members)

@app.route('/cell-teams/<int:team_id>/add-member', methods=['POST'])
@login_required
def add_team_member():
    team_id = request.form.get('team_id')
    member_id = request.form.get('member_id')
    
    team = CellTeam.query.get_or_404(team_id)
    member = Member.query.get_or_404(member_id)
    
    if member not in team.members:
        team.members.append(member)
        try:
            db.session.commit()
            flash(f'{member.first_name} {member.last_name} added to {team.name}!')
        except Exception as e:
            db.session.rollback()
            flash('Error adding member to team: ' + str(e))
    
    return redirect(url_for('cell_team_details', team_id=team_id))

@app.route('/cell-teams/<int:team_id>/remove-member/<int:member_id>', methods=['POST'])
@login_required
def remove_team_member(team_id, member_id):
    team = CellTeam.query.get_or_404(team_id)
    member = Member.query.get_or_404(member_id)
    
    if member in team.members:
        team.members.remove(member)
        try:
            db.session.commit()
            flash(f'{member.first_name} {member.last_name} removed from {team.name}!')
        except Exception as e:
            db.session.rollback()
            flash('Error removing member from team: ' + str(e))
    
    return redirect(url_for('cell_team_details', team_id=team_id))

@app.route('/documents')
@login_required
def documents():
    search_query = request.args.get('search', '').strip()
    doc_type = request.args.get('type', '').strip()
    
    query = Document.query
    
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            or_(
                Document.title.ilike(search),
                Document.content.ilike(search),
                Document.tags.ilike(search)
            )
        )
    
    if doc_type:
        query = query.filter_by(document_type=doc_type)
    
    documents = query.order_by(Document.created_at.desc()).all()
    return render_template('documents.html', documents=documents, search_query=search_query, current_type=doc_type)

@app.route('/documents/create', methods=['GET', 'POST'])
@login_required
def create_document():
    if request.method == 'POST':
        title = request.form.get('title')
        document_type = request.form.get('document_type')
        content = request.form.get('content')
        tags = request.form.get('tags')
        related_members = request.form.getlist('related_members')
        
        # Handle file upload
        file = request.files.get('document_file')
        file_path = None
        if file and file.filename:
            # Secure the filename
            filename = secure_filename(file.filename)
            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join(app.root_path, 'uploads')
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
            # Save the file
            file_path = os.path.join('uploads', filename)
            file.save(os.path.join(app.root_path, file_path))
        
        document = Document(
            title=title,
            document_type=document_type,
            content=content,
            file_path=file_path,
            created_by=current_user.id,
            tags=tags,
            related_members=','.join(related_members) if related_members else None
        )
        
        try:
            db.session.add(document)
            db.session.commit()
            flash('Document created successfully!')
            return redirect(url_for('documents'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating document: ' + str(e))
    
    members = Member.query.all()
    return render_template('create_document.html', members=members)

@app.route('/documents/<int:doc_id>')
@login_required
def document_details(doc_id):
    document = Document.query.get_or_404(doc_id)
    related_members = []
    if document.related_members:
        member_ids = [int(id) for id in document.related_members.split(',')]
        related_members = Member.query.filter(Member.id.in_(member_ids)).all()
    return render_template('document_details.html', document=document, related_members=related_members)

@app.route('/documents/<int:doc_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    
    if request.method == 'POST':
        document.title = request.form.get('title')
        document.document_type = request.form.get('document_type')
        document.content = request.form.get('content')
        document.tags = request.form.get('tags')
        document.related_members = ','.join(request.form.getlist('related_members'))
        
        # Handle file upload
        file = request.files.get('document_file')
        if file and file.filename:
            # Delete old file if it exists
            if document.file_path:
                old_file_path = os.path.join(app.root_path, document.file_path)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Save new file
            filename = secure_filename(file.filename)
            uploads_dir = os.path.join(app.root_path, 'uploads')
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
            file_path = os.path.join('uploads', filename)
            file.save(os.path.join(app.root_path, file_path))
            document.file_path = file_path
        
        try:
            db.session.commit()
            flash('Document updated successfully!')
            return redirect(url_for('document_details', doc_id=doc_id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating document: ' + str(e))
    
    members = Member.query.all()
    selected_members = document.related_members.split(',') if document.related_members else []
    return render_template('edit_document.html', document=document, members=members, selected_members=selected_members)

@app.route('/marriages')
@login_required
def marriages():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    query = Marriage.query
    
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            or_(
                Marriage.bride_name.ilike(search),
                Marriage.groom_name.ilike(search),
                Marriage.venue.ilike(search),
                Marriage.service_type.ilike(search)
            )
        )
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    marriages = query.order_by(Marriage.wedding_date.desc()).all()
    return render_template('marriages.html', marriages=marriages, search_query=search_query, current_status=status_filter)

@app.route('/api/search_members')
@login_required
def search_members():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    search = f"%{query}%"
    members = Member.query.filter(
        or_(
            Member.first_name.ilike(search),
            Member.last_name.ilike(search),
            Member.email.ilike(search)
        )
    ).limit(10).all()
    
    return jsonify([{
        'id': member.id,
        'name': f"{member.first_name} {member.last_name}",
        'email': member.email
    } for member in members])

@app.route('/marriages/create', methods=['GET', 'POST'])
@login_required
def create_marriage():
    if request.method == 'POST':
        # Get bride and groom
        bride = Member.query.get(request.form.get('bride_id'))
        groom = Member.query.get(request.form.get('groom_id'))
        
        if not bride or not groom:
            flash('Please select both bride and groom from the member list.')
            return redirect(url_for('create_marriage'))
        
        # Get required courses
        required_courses = request.form.getlist('required_courses')
        
        # Calculate waiting period end date (e.g., 6 months from application)
        application_date = datetime.strptime(request.form.get('application_date'), '%Y-%m-%d').date()
        waiting_period_end = application_date + timedelta(days=180)  # 6 months
        
        marriage = Marriage(
            bride_id=bride.id,
            groom_id=groom.id,
            wedding_date=datetime.strptime(request.form.get('wedding_date'), '%Y-%m-%d').date(),
            venue=request.form.get('venue'),
            service_type=request.form.get('service_type'),
            required_courses=json.dumps(required_courses),
            completed_courses=json.dumps([]),
            next_course_date=datetime.strptime(request.form.get('next_course_date'), '%Y-%m-%d').date() if request.form.get('next_course_date') else None,
            course_notes=request.form.get('course_notes'),
            application_date=application_date,
            waiting_period_end=waiting_period_end,
            waiting_period_status=request.form.get('waiting_period_status'),
            waiver_reason=request.form.get('waiver_reason'),
            counseling_status=request.form.get('counseling_status'),
            counseling_notes=request.form.get('counseling_notes'),
            next_counseling_date=datetime.strptime(request.form.get('next_counseling_date'), '%Y-%m-%d').date() if request.form.get('next_counseling_date') else None,
            counseling_sessions_completed=0,
            parents_approval=bool(request.form.get('parents_approval')),
            officiating_minister=request.form.get('officiating_minister'),
            witnesses=request.form.get('witnesses'),
            special_requirements=request.form.get('special_requirements'),
            status='Pending'
        )
        
        try:
            db.session.add(marriage)
            db.session.commit()
            flash('Marriage service request created successfully!')
            return redirect(url_for('marriages'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating marriage service request: ' + str(e))
    
    return render_template('create_marriage.html')

@app.route('/marriages/<int:marriage_id>')
@login_required
def marriage_details(marriage_id):
    marriage = Marriage.query.get_or_404(marriage_id)
    return render_template('marriage_details.html', marriage=marriage)

@app.route('/marriages/<int:marriage_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_marriage(marriage_id):
    marriage = Marriage.query.get_or_404(marriage_id)
    
    if request.method == 'POST':
        marriage.bride_name = request.form.get('bride_name')
        marriage.groom_name = request.form.get('groom_name')
        marriage.wedding_date = datetime.strptime(request.form.get('wedding_date'), '%Y-%m-%d').date()
        marriage.venue = request.form.get('venue')
        marriage.service_type = request.form.get('service_type')
        marriage.counseling_status = request.form.get('counseling_status')
        marriage.counseling_notes = request.form.get('counseling_notes')
        marriage.bride_contact = request.form.get('bride_contact')
        marriage.groom_contact = request.form.get('groom_contact')
        marriage.parents_approval = bool(request.form.get('parents_approval'))
        marriage.officiating_minister = request.form.get('officiating_minister')
        marriage.witnesses = request.form.get('witnesses')
        marriage.special_requirements = request.form.get('special_requirements')
        marriage.status = request.form.get('status')
        
        try:
            db.session.commit()
            flash('Marriage service details updated successfully!')
            return redirect(url_for('marriage_details', marriage_id=marriage_id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating marriage service details: ' + str(e))
    
    return render_template('edit_marriage.html', marriage=marriage)

@app.route('/marriages/analytics')
@login_required
def marriage_analytics():
    # Get total marriages
    total_marriages = Marriage.query.count()
    
    # Get marriages by status
    status_counts = db.session.query(
        Marriage.status, 
        db.func.count(Marriage.id)
    ).group_by(Marriage.status).all()
    
    # Get marriages by month (last 12 months)
    current_date = datetime.utcnow()
    last_year = current_date - timedelta(days=365)
    monthly_marriages = db.session.query(
        db.func.strftime('%Y-%m', Marriage.wedding_date).label('month'),
        db.func.count(Marriage.id)
    ).filter(Marriage.wedding_date >= last_year).group_by('month').all()
    
    # Get course completion stats
    total_with_courses = Marriage.query.filter(Marriage.required_courses != '[]').count()
    completed_courses = Marriage.query.filter(
        Marriage.required_courses != '[]',
        Marriage.completed_courses != '[]'
    ).count()
    
    # Get counseling stats
    counseling_stats = db.session.query(
        Marriage.counseling_status,
        db.func.count(Marriage.id)
    ).group_by(Marriage.counseling_status).all()
    
    # Get average waiting period
    avg_waiting_period = db.session.query(
        db.func.avg(
            db.func.julianday(Marriage.wedding_date) - 
            db.func.julianday(Marriage.application_date)
        )
    ).scalar()
    
    # Get venue statistics
    venue_stats = db.session.query(
        Marriage.venue,
        db.func.count(Marriage.id)
    ).group_by(Marriage.venue).all()
    
    # Get service type distribution
    service_types = db.session.query(
        Marriage.service_type,
        db.func.count(Marriage.id)
    ).group_by(Marriage.service_type).all()
    
    return render_template(
        'marriage_analytics.html',
        total_marriages=total_marriages,
        status_counts=status_counts,
        monthly_marriages=monthly_marriages,
        total_with_courses=total_with_courses,
        completed_courses=completed_courses,
        counseling_stats=counseling_stats,
        avg_waiting_period=avg_waiting_period,
        venue_stats=venue_stats,
        service_types=service_types
    )

@app.route('/notifications')
@login_required
def notifications():
    # Get unread notifications
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).all()
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify([{
            'id': notification.id,
            'type': notification.type,
            'title': notification.title,
            'message': notification.message,
            'date': notification.date.strftime('%Y-%m-%d') if notification.date else None,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for notification in notifications])
    
    # For regular requests, return the HTML template
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/mark-read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
    return jsonify({'success': True})

@app.route('/notifications/count')
@login_required
def notification_count():
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    return jsonify({'count': count})

@app.route('/appointments')
@login_required
def appointments():
    # Get filter parameters
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    date_filter = request.args.get('date', '')
    
    # Base query
    query = Appointment.query
    
    # Apply filters
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(appointment_type=type_filter)
    if date_filter:
        date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        query = query.filter_by(date=date)
    
    # Get appointments
    if current_user.is_admin:
        appointments = query.order_by(Appointment.date.desc()).all()
    else:
        appointments = query.filter_by(counselor_id=current_user.id).order_by(Appointment.date.desc()).all()
    
    return render_template('appointments.html', 
                         appointments=appointments,
                         status_filter=status_filter,
                         type_filter=type_filter,
                         date_filter=date_filter)

@app.route('/appointments/create', methods=['GET', 'POST'])
@login_required
def create_appointment():
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        counselor_id = request.form.get('counselor_id')
        appointment_type = request.form.get('appointment_type')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        time = request.form.get('time')
        duration = int(request.form.get('duration', 60))
        reason = request.form.get('reason')
        notes = request.form.get('notes')
        
        # Check for time conflicts
        existing_appointment = Appointment.query.filter_by(
            counselor_id=counselor_id,
            date=date,
            time=time
        ).first()
        
        if existing_appointment:
            flash('This time slot is already booked. Please choose another time.')
            return redirect(url_for('create_appointment'))
        
        appointment = Appointment(
            member_id=member_id,
            counselor_id=counselor_id,
            appointment_type=appointment_type,
            date=date,
            time=time,
            duration=duration,
            reason=reason,
            notes=notes,
            status='Pending'
        )
        
        try:
            db.session.add(appointment)
            db.session.commit()
            flash('Appointment scheduled successfully!')
            return redirect(url_for('appointments'))
        except Exception as e:
            db.session.rollback()
            flash('Error scheduling appointment: ' + str(e))
    
    # Get list of counselors for the form
    counselors = User.query.filter_by(is_admin=True).all()
    
    return render_template('create_appointment.html',
                         counselors=counselors)

@app.route('/appointments/<int:appointment_id>')
@login_required
def appointment_details(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('appointment_details.html', appointment=appointment)

@app.route('/appointments/<int:appointment_id>/update-status', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    new_status = request.form.get('status')
    
    if new_status in ['Pending', 'Confirmed', 'Completed', 'Cancelled']:
        appointment.status = new_status
        db.session.commit()
        flash('Appointment status updated successfully!')
    
    return redirect(url_for('appointment_details', appointment_id=appointment_id))

def check_upcoming_events():
    """Check for upcoming birthdays and anniversaries"""
    today = datetime.utcnow().date()
    
    # Check birthdays (7 days in advance)
    upcoming_birthdays = Member.query.filter(
        db.func.strftime('%m-%d', Member.date_of_birth) >= db.func.strftime('%m-%d', today),
        db.func.strftime('%m-%d', Member.date_of_birth) <= db.func.strftime('%m-%d', today + timedelta(days=7))
    ).all()
    
    # Check anniversaries (7 days in advance)
    upcoming_marriages = Marriage.query.filter(
        db.func.strftime('%m-%d', Marriage.wedding_date) >= db.func.strftime('%m-%d', today),
        db.func.strftime('%m-%d', Marriage.wedding_date) <= db.func.strftime('%m-%d', today + timedelta(days=7))
    ).all()
    
    # Create notifications for staff
    staff_users = User.query.filter_by(is_admin=True).all()
    
    for member in upcoming_birthdays:
        birthday = member.date_of_birth.replace(year=today.year)
        days_until = (birthday - today).days
        
        for user in staff_users:
            # Check if notification already exists
            existing = Notification.query.filter_by(
                type='birthday',
                reference_id=member.id,
                user_id=user.id,
                is_read=False
            ).first()
            
            if not existing:
                notification = Notification(
                    type='birthday',
                    title=f"Upcoming Birthday: {member.first_name} {member.last_name}",
                    message=f"Birthday in {days_until} days ({birthday.strftime('%B %d')})",
                    date=birthday,
                    user_id=user.id,
                    reference_id=member.id
                )
                db.session.add(notification)
    
    for marriage in upcoming_marriages:
        anniversary = marriage.wedding_date.replace(year=today.year)
        days_until = (anniversary - today).days
        years = today.year - marriage.wedding_date.year
        
        for user in staff_users:
            existing = Notification.query.filter_by(
                type='anniversary',
                reference_id=marriage.id,
                user_id=user.id,
                is_read=False
            ).first()
            
            if not existing:
                notification = Notification(
                    type='anniversary',
                    title=f"Wedding Anniversary: {marriage.bride.first_name} & {marriage.groom.first_name}",
                    message=f"{years}th Anniversary in {days_until} days ({anniversary.strftime('%B %d')})",
                    date=anniversary,
                    user_id=user.id,
                    reference_id=marriage.id
                )
                db.session.add(notification)
    
    db.session.commit()

# Add notification check to before_request
@app.before_request
def before_request():
    if current_user.is_authenticated:
        check_upcoming_events()

@app.route('/finance')
@login_required
def finance_dashboard():
    # Get summary statistics
    total_income = db.session.query(db.func.sum(FinanceTransaction.amount)).\
        filter(FinanceTransaction.transaction_type == 'income').scalar() or 0
    total_expense = db.session.query(db.func.sum(FinanceTransaction.amount)).\
        filter(FinanceTransaction.transaction_type == 'expense').scalar() or 0
    current_balance = total_income - total_expense
    
    # Get recent transactions
    recent_transactions = FinanceTransaction.query.\
        order_by(FinanceTransaction.transaction_date.desc()).limit(5).all()
    
    # Get category summaries
    income_by_category = db.session.query(
        FinanceCategory.name,
        db.func.sum(FinanceTransaction.amount)
    ).join(FinanceTransaction).\
        filter(FinanceTransaction.transaction_type == 'income').\
        group_by(FinanceCategory.name).all()
    
    expense_by_category = db.session.query(
        FinanceCategory.name,
        db.func.sum(FinanceTransaction.amount)
    ).join(FinanceTransaction).\
        filter(FinanceTransaction.transaction_type == 'expense').\
        group_by(FinanceCategory.name).all()
    
    return render_template('finance/dashboard.html',
                         total_income=total_income,
                         total_expense=total_expense,
                         current_balance=current_balance,
                         recent_transactions=recent_transactions,
                         income_by_category=income_by_category,
                         expense_by_category=expense_by_category)

@app.route('/finance/transactions')
@login_required
def finance_transactions():
    page = request.args.get('page', 1, type=int)
    transaction_type = request.args.get('type', 'all')
    category_id = request.args.get('category', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = FinanceTransaction.query
    
    # Apply filters
    if transaction_type != 'all':
        query = query.filter_by(transaction_type=transaction_type)
    if category_id != 'all':
        query = query.filter_by(category_id=category_id)
    if start_date:
        query = query.filter(FinanceTransaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(FinanceTransaction.transaction_date <= end_date)
    
    transactions = query.order_by(FinanceTransaction.transaction_date.desc()).\
        paginate(page=page, per_page=20, error_out=False)
    
    categories = FinanceCategory.query.all()
    
    return render_template('finance/transactions.html',
                         transactions=transactions,
                         categories=categories)

@app.route('/finance/transactions/create', methods=['GET', 'POST'])
@login_required
def create_transaction():
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        amount = float(request.form.get('amount'))
        transaction_type = request.form.get('transaction_type')
        payment_method = request.form.get('payment_method')
        reference_number = request.form.get('reference_number')
        description = request.form.get('description')
        transaction_date = datetime.strptime(request.form.get('transaction_date'), '%Y-%m-%d').date()
        
        transaction = FinanceTransaction(
            category_id=category_id,
            amount=amount,
            transaction_type=transaction_type,
            payment_method=payment_method,
            reference_number=reference_number,
            description=description,
            transaction_date=transaction_date,
            recorded_by=current_user.id
        )
        
        # Additional fields for offerings/tithes
        if transaction_type == 'income':
            transaction.service_type = request.form.get('service_type')
            transaction.envelope_number = request.form.get('envelope_number')
            transaction.donor_name = request.form.get('donor_name')
            transaction.is_anonymous = bool(request.form.get('is_anonymous'))
        
        # Additional fields for expenses
        if transaction_type == 'expense':
            transaction.vendor_name = request.form.get('vendor_name')
            transaction.receipt_number = request.form.get('receipt_number')
        
        try:
            db.session.add(transaction)
            db.session.commit()
            flash('Transaction recorded successfully!')
            return redirect(url_for('finance_transactions'))
        except Exception as e:
            db.session.rollback()
            flash('Error recording transaction: ' + str(e))
    
    categories = FinanceCategory.query.all()
    return render_template('finance/create_transaction.html', categories=categories)

@app.route('/finance/reports')
@login_required
def finance_reports():
    reports = FinancialReport.query.order_by(FinancialReport.generated_at.desc()).all()
    return render_template('finance/reports.html', reports=reports)

@app.route('/finance/reports/generate', methods=['GET', 'POST'])
@login_required
def generate_report():
    if request.method == 'POST':
        report_type = request.form.get('report_type')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        
        # Calculate totals
        income = db.session.query(db.func.sum(FinanceTransaction.amount)).\
            filter(FinanceTransaction.transaction_type == 'income',
                   FinanceTransaction.transaction_date.between(start_date, end_date)).scalar() or 0
        
        expense = db.session.query(db.func.sum(FinanceTransaction.amount)).\
            filter(FinanceTransaction.transaction_type == 'expense',
                   FinanceTransaction.transaction_date.between(start_date, end_date)).scalar() or 0
        
        # Get detailed breakdown
        breakdown = db.session.query(
            FinanceCategory.name,
            FinanceTransaction.transaction_type,
            db.func.sum(FinanceTransaction.amount)
        ).join(FinanceTransaction).\
            filter(FinanceTransaction.transaction_date.between(start_date, end_date)).\
            group_by(FinanceCategory.name, FinanceTransaction.transaction_type).all()
        
        report = FinancialReport(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            total_income=income,
            total_expense=expense,
            balance=income - expense,
            generated_by=current_user.id,
            report_data=json.dumps([{
                'category': item[0],
                'type': item[1],
                'amount': float(item[2])
            } for item in breakdown])
        )
        
        try:
            db.session.add(report)
            db.session.commit()
            flash('Report generated successfully!')
            return redirect(url_for('finance_reports'))
        except Exception as e:
            db.session.rollback()
            flash('Error generating report: ' + str(e))
    
    return render_template('finance/generate_report.html')

@app.route('/finance/categories')
@login_required
def finance_categories():
    categories = FinanceCategory.query.all()
    return render_template('finance/categories.html', categories=categories)

@app.route('/finance/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    if request.method == 'POST':
        category = FinanceCategory(
            name=request.form.get('name'),
            type=request.form.get('type'),
            description=request.form.get('description')
        )
        
        try:
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!')
            return redirect(url_for('finance_categories'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating category: ' + str(e))
    
    return render_template('finance/create_category.html')

@app.route('/finance/budgets')
@login_required
def budgets():
    current_year = datetime.utcnow().year
    selected_year = request.args.get('year', current_year, type=int)
    
    # Get annual budgets
    annual_budgets = Budget.query.filter_by(year=selected_year, month=None).all()
    
    # Get monthly budgets
    monthly_budgets = Budget.query.filter_by(year=selected_year).filter(Budget.month != None).all()
    
    # Calculate totals
    total_budget = sum(budget.amount for budget in annual_budgets + monthly_budgets)
    total_actual = sum(budget.actual_amount for budget in annual_budgets + monthly_budgets)
    total_variance = total_actual - total_budget
    
    return render_template('finance/budgets.html',
                         annual_budgets=annual_budgets,
                         monthly_budgets=monthly_budgets,
                         total_budget=total_budget,
                         total_actual=total_actual,
                         total_variance=total_variance,
                         current_year=current_year,
                         selected_year=selected_year)

@app.route('/finance/budgets/create', methods=['GET', 'POST'])
@login_required
def create_budget():
    if request.method == 'POST':
        budget = Budget(
            category_id=request.form.get('category_id'),
            year=int(request.form.get('year')),
            month=int(request.form.get('month')) if request.form.get('month') else None,
            amount=float(request.form.get('amount')),
            notes=request.form.get('notes'),
            created_by=current_user.id
        )
        
        try:
            db.session.add(budget)
            db.session.commit()
            flash('Budget created successfully!')
            return redirect(url_for('budgets'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating budget: ' + str(e))
    
    categories = FinanceCategory.query.all()
    current_year = datetime.utcnow().year
    return render_template('finance/create_budget.html', categories=categories, current_year=current_year)

# Add this after creating the Flask app
@app.template_filter('month_name')
def month_name_filter(month_number):
    return calendar.month_name[month_number] if month_number else ''

# Teaching Service Models
class TeachingProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    program_type = db.Column(db.String(50), nullable=False)  # 'sunday_school', 'youth', 'children', 'bible_study'
    description = db.Column(db.Text)
    age_group = db.Column(db.String(50))  # e.g., '3-5 years', '13-19 years'
    schedule = db.Column(db.String(100))  # e.g., 'Every Sunday 9:00 AM'
    location = db.Column(db.String(200))
    coordinator_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, inactive
    
    # Relationships
    coordinator = db.relationship('Member', backref='coordinated_programs')
    teachers = db.relationship('TeachingTeacher', back_populates='program')
    students = db.relationship('TeachingStudent', back_populates='program')

class TeachingTeacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('teaching_program.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    role = db.Column(db.String(50))  # lead teacher, assistant, volunteer
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)
    
    # Relationships
    program = db.relationship('TeachingProgram', back_populates='teachers')
    teacher = db.relationship('Member', backref='teaching_roles')

class TeachingStudent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('teaching_program.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow)
    parent_contact = db.Column(db.String(100))
    emergency_contact = db.Column(db.String(100))
    medical_info = db.Column(db.Text)
    attendance_record = db.Column(db.Text)  # JSON string of attendance dates
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)
    
    # Relationships
    program = db.relationship('TeachingProgram', back_populates='students')
    student = db.relationship('Member', backref='enrolled_programs')

class TeachingMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('teaching_program.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    material_type = db.Column(db.String(50))  # lesson_plan, worksheet, activity, resource
    file_path = db.Column(db.String(500))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    
    # Relationships
    program = db.relationship('TeachingProgram', backref='materials')
    creator = db.relationship('User', backref='created_materials')

class TeachingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('teaching_program.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50))  # class, activity, field_trip, competition
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(50))
    location = db.Column(db.String(200))
    coordinator_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    max_participants = db.Column(db.Integer)
    requirements = db.Column(db.Text)
    status = db.Column(db.String(20), default='upcoming')  # upcoming, ongoing, completed, cancelled
    
    # Relationships
    program = db.relationship('TeachingProgram', backref='events')
    coordinator = db.relationship('Member', backref='coordinated_events')

@app.route('/teaching')
@login_required
def teaching_dashboard():
    programs = TeachingProgram.query.all()
    upcoming_events = TeachingEvent.query.filter(
        TeachingEvent.date >= datetime.utcnow().date(),
        TeachingEvent.status == 'upcoming'
    ).order_by(TeachingEvent.date).limit(5).all()
    
    # Get statistics
    total_students = TeachingStudent.query.filter_by(status='active').count()
    total_teachers = TeachingTeacher.query.filter_by(status='active').count()
    active_programs = TeachingProgram.query.filter_by(status='active').count()
    
    return render_template('teaching/dashboard.html',
                         programs=programs,
                         upcoming_events=upcoming_events,
                         total_students=total_students,
                         total_teachers=total_teachers,
                         active_programs=active_programs)

@app.route('/teaching/programs')
@login_required
def teaching_programs():
    programs = TeachingProgram.query.all()
    return render_template('teaching/programs.html', programs=programs)

@app.route('/teaching/programs/create', methods=['GET', 'POST'])
@login_required
def create_program():
    if request.method == 'POST':
        program = TeachingProgram(
            name=request.form.get('name'),
            program_type=request.form.get('program_type'),
            description=request.form.get('description'),
            age_group=request.form.get('age_group'),
            schedule=request.form.get('schedule'),
            location=request.form.get('location'),
            coordinator_id=request.form.get('coordinator_id')
        )
        
        try:
            db.session.add(program)
            db.session.commit()
            flash('Program created successfully!')
            return redirect(url_for('teaching_programs'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating program: ' + str(e))
    
    coordinators = Member.query.all()
    return render_template('teaching/create_program.html', coordinators=coordinators)

@app.route('/teaching/teachers')
@login_required
def teaching_teachers():
    teachers = TeachingTeacher.query.filter_by(status='active').all()
    programs = TeachingProgram.query.all()
    return render_template('teaching/teachers.html', teachers=teachers, programs=programs)

@app.route('/teaching/teachers/assign', methods=['GET', 'POST'])
@login_required
def assign_teacher():
    if request.method == 'POST':
        teacher = TeachingTeacher(
            program_id=request.form.get('program_id'),
            teacher_id=request.form.get('teacher_id'),
            role=request.form.get('role'),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None,
            notes=request.form.get('notes')
        )
        
        try:
            db.session.add(teacher)
            db.session.commit()
            flash('Teacher assigned successfully!')
            return redirect(url_for('teaching_teachers'))
        except Exception as e:
            db.session.rollback()
            flash('Error assigning teacher: ' + str(e))
    
    programs = TeachingProgram.query.all()
    teachers = Member.query.all()
    return render_template('teaching/assign_teacher.html', programs=programs, teachers=teachers)

@app.route('/teaching/students')
@login_required
def teaching_students():
    students = TeachingStudent.query.filter_by(status='active').all()
    programs = TeachingProgram.query.all()
    return render_template('teaching/students.html', students=students, programs=programs)

@app.route('/teaching/students/enroll', methods=['GET', 'POST'])
@login_required
def enroll_student():
    if request.method == 'POST':
        student = TeachingStudent(
            program_id=request.form.get('program_id'),
            student_id=request.form.get('student_id'),
            parent_contact=request.form.get('parent_contact'),
            emergency_contact=request.form.get('emergency_contact'),
            medical_info=request.form.get('medical_info'),
            notes=request.form.get('notes')
        )
        
        try:
            db.session.add(student)
            db.session.commit()
            flash('Student enrolled successfully!')
            return redirect(url_for('teaching_students'))
        except Exception as e:
            db.session.rollback()
            flash('Error enrolling student: ' + str(e))
    
    programs = TeachingProgram.query.all()
    students = Member.query.all()
    return render_template('teaching/enroll_student.html', programs=programs, students=students)

@app.route('/teaching/materials')
@login_required
def teaching_materials():
    materials = TeachingMaterial.query.order_by(TeachingMaterial.created_at.desc()).all()
    programs = TeachingProgram.query.all()
    return render_template('teaching/materials.html', materials=materials, programs=programs)

@app.route('/teaching/materials/create', methods=['GET', 'POST'])
@login_required
def create_material():
    if request.method == 'POST':
        file = request.files.get('material_file')
        file_path = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            uploads_dir = os.path.join(app.root_path, 'uploads', 'teaching')
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
            file_path = os.path.join('uploads', 'teaching', filename)
            file.save(os.path.join(app.root_path, file_path))
        
        material = TeachingMaterial(
            program_id=request.form.get('program_id'),
            title=request.form.get('title'),
            description=request.form.get('description'),
            material_type=request.form.get('material_type'),
            file_path=file_path,
            created_by=current_user.id
        )
        
        try:
            db.session.add(material)
            db.session.commit()
            flash('Material created successfully!')
            return redirect(url_for('teaching_materials'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating material: ' + str(e))
    
    programs = TeachingProgram.query.all()
    return render_template('teaching/create_material.html', programs=programs)

@app.route('/teaching/events')
@login_required
def teaching_events():
    events = TeachingEvent.query.order_by(TeachingEvent.date).all()
    return render_template('teaching/events.html', events=events)

@app.route('/teaching/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        event = TeachingEvent(
            program_id=request.form.get('program_id'),
            title=request.form.get('title'),
            description=request.form.get('description'),
            event_type=request.form.get('event_type'),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            time=request.form.get('time'),
            location=request.form.get('location'),
            coordinator_id=request.form.get('coordinator_id'),
            max_participants=request.form.get('max_participants'),
            requirements=request.form.get('requirements')
        )
        
        try:
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!')
            return redirect(url_for('teaching_events'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating event: ' + str(e))
    
    programs = TeachingProgram.query.all()
    coordinators = Member.query.all()
    return render_template('teaching/create_event.html', programs=programs, coordinators=coordinators)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', password='admin123', is_admin=True)
            db.session.add(admin)
            
            # Create a test notification for the admin
            notification = Notification(
                type='welcome',
                title='Welcome to EPAPHRA',
                message='Welcome to your church management system!',
                date=datetime.utcnow().date(),
                user_id=1,  # This will be the admin's ID
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
            
            try:
                db.session.commit()
                print("Database initialized successfully with admin user and test notification")
            except Exception as e:
                db.session.rollback()
                print("Error initializing database:", str(e))
    
    app.run(debug=True, port=3001) 