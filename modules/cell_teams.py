from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, CellTeam, CellTeamMember
from datetime import datetime

cell_teams_bp = Blueprint('cell_teams', __name__, url_prefix='/cell-teams')

@cell_teams_bp.route('/')
@login_required
def index():
    all_teams = CellTeam.query.all()
    return render_template('cell_teams/index.html', teams=all_teams)

@cell_teams_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        location = request.form.get('location')
        meeting_day = request.form.get('meeting_day')
        meeting_time = request.form.get('meeting_time')
        
        try:
            cell_team = CellTeam(
                name=name,
                description=description,
                location=location,
                meeting_day=meeting_day,
                meeting_time=meeting_time,
                leader_id=current_user.id,
                created_at=datetime.now()
            )
            
            db.session.add(cell_team)
            db.session.commit()
            
            flash('Cell team created successfully!', 'success')
            return redirect(url_for('cell_teams.index'))
            
        except Exception as e:
            flash('Error creating cell team. Please try again.', 'error')
            return render_template('create_cell_team.html')
    
    return render_template('create_cell_team.html') 