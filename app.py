from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from sqlalchemy import or_

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