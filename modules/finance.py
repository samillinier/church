from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Transaction, Budget, Category
from datetime import datetime

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')

@finance_bp.route('/')
@login_required
def index():
    transactions = Transaction.query.all()
    budgets = Budget.query.all()
    categories = Category.query.all()
    return render_template('finance/index.html', 
                         transactions=transactions,
                         budgets=budgets,
                         categories=categories)

@finance_bp.route('/transaction/create', methods=['GET', 'POST'])
@login_required
def create_transaction():
    if request.method == 'POST':
        amount = request.form.get('amount')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        transaction_type = request.form.get('type')
        
        try:
            transaction = Transaction(
                amount=float(amount),
                description=description,
                category_id=category_id,
                type=transaction_type,
                created_by=current_user.id,
                created_at=datetime.now()
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            flash('Transaction recorded successfully!', 'success')
            return redirect(url_for('finance.index'))
            
        except Exception as e:
            flash('Error recording transaction. Please try again.', 'error')
            return render_template('finance/create_transaction.html')
    
    categories = Category.query.all()
    return render_template('finance/create_transaction.html', categories=categories) 