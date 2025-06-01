from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from models import db, Document
from datetime import datetime
import os

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/')
@login_required
def index():
    documents = Document.query.all()
    return render_template('documents/index.html', documents=documents)

@documents_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            try:
                # Save file
                filename = file.filename
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # Create document record
                document = Document(
                    title=request.form.get('title'),
                    description=request.form.get('description'),
                    file_path=file_path,
                    uploaded_by=current_user.id,
                    uploaded_at=datetime.now()
                )
                
                db.session.add(document)
                db.session.commit()
                
                flash('Document uploaded successfully!', 'success')
                return redirect(url_for('documents.index'))
                
            except Exception as e:
                flash('Error uploading document. Please try again.', 'error')
                return render_template('upload_document.html')
    
    return render_template('upload_document.html') 