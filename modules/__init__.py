from flask import Blueprint

# Import all blueprints
from .appointments import appointments_bp
from .cell_teams import cell_teams_bp
from .documents import documents_bp
from .finance import finance_bp
from .members import members_bp

# List of all blueprints to register
all_blueprints = [
    appointments_bp,
    cell_teams_bp,
    documents_bp,
    finance_bp,
    members_bp
] 