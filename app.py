from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from sqlalchemy import or_
import os
from werkzeug.utils import secure_filename
import json

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
            Member.email.ilike(search),
            Member.phone.ilike(search)
        )
    ).limit(10).all()
    
    return jsonify([{
        'id': member.id,
        'first_name': member.first_name,
        'last_name': member.last_name,
        'email': member.email,
        'phone': member.phone,
        'membership_status': member.membership_status
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', password='admin123', is_admin=True)
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True, port=8080) 