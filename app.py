from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Cigarette
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')

# Fix for SQLite URL on Render
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('onboarding'))
    
    return render_template('register.html')

@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.age = int(request.form['age'])
        current_user.cigs_per_day = int(request.form['cigs_per_day'])
        current_user.cost_per_cig = float(request.form['cost_per_cig'])
        current_user.currency = request.form['currency']
        current_user.cigs_per_pack = int(request.form['cigs_per_pack'])
        
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('onboarding.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.name:
        return redirect(url_for('onboarding'))
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Items per page
    sort_by = request.args.get('sort', 'smoked_at')  # Default sort by date
    order = request.args.get('order', 'desc')  # Default order descending
    date_filter = request.args.get('date')  # Date filter
    
    # Base query
    query = Cigarette.query.filter_by(user_id=current_user.id)
    
    # Apply date filter if present
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d')
            query = query.filter(
                db.func.date(Cigarette.smoked_at) == filter_date.date()
            )
        except ValueError:
            flash('Invalid date format')
    
    # Apply sorting
    if sort_by == 'smoked_at':
        query = query.order_by(
            Cigarette.smoked_at.desc() if order == 'desc' else Cigarette.smoked_at.asc()
        )
    elif sort_by == 'cost':
        query = query.order_by(
            Cigarette.cost.desc() if order == 'desc' else Cigarette.cost.asc()
        )
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    cigarettes = pagination.items
    
    # Calculate statistics
    total_cigarettes = query.count()
    total_spent = sum(cig.cost for cig in query.all())
    
    # Calculate money saved
    if cigarettes:
        # Calculate total savings
        days_since_start = (datetime.utcnow() - current_user.created_at).days + 1
        expected_total_cost = days_since_start * current_user.cigs_per_day * current_user.cost_per_cig
        total_money_saved = expected_total_cost - total_spent
        
        # Calculate today's savings
        today = datetime.utcnow().date()
        today_cigarettes = query.filter(
            db.func.date(Cigarette.smoked_at) == today
        ).all()
        today_spent = sum(cig.cost for cig in today_cigarettes)
        today_expected_cost = current_user.cigs_per_day * current_user.cost_per_cig
        today_money_saved = today_expected_cost - today_spent
    else:
        total_money_saved = 0
        today_money_saved = 0
    
    # Calculate average time between cigarettes
    if len(cigarettes) > 1:
        time_diffs = []
        sorted_cigs = sorted(cigarettes, key=lambda x: x.smoked_at)
        for i in range(len(sorted_cigs)-1):
            diff = sorted_cigs[i].smoked_at - sorted_cigs[i+1].smoked_at
            time_diffs.append(abs(diff.total_seconds() / 3600))  # Convert to hours
        avg_time_between = sum(time_diffs) / len(time_diffs)
        max_time_between = max(time_diffs) if time_diffs else 0
    else:
        avg_time_between = 0
        max_time_between = 0
    
    return render_template('dashboard.html',
                         cigarettes=cigarettes,
                         pagination=pagination,
                         total_cigarettes=total_cigarettes,
                         total_spent=total_spent,
                         total_money_saved=total_money_saved,
                         today_money_saved=today_money_saved,
                         avg_time_between=avg_time_between,
                         max_time_between=max_time_between,
                         current_sort=sort_by,
                         current_order=order,
                         current_date=date_filter)

@app.route('/add_cigarette', methods=['POST'])
@login_required
def add_cigarette():
    cigarette = Cigarette(
        user_id=current_user.id,
        cost=current_user.cost_per_cig
    )
    db.session.add(cigarette)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_cigarette/<int:id>')
@login_required
def delete_cigarette(id):
    cigarette = Cigarette.query.get_or_404(id)
    if cigarette.user_id == current_user.id:
        db.session.delete(cigarette)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/edit_cigarette/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_cigarette(id):
    cigarette = Cigarette.query.get_or_404(id)
    if cigarette.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            new_cost = float(request.form['cost'])
            new_date = datetime.strptime(request.form['smoked_at'], '%Y-%m-%dT%H:%M')
            
            cigarette.cost = new_cost
            cigarette.smoked_at = new_date
            db.session.commit()
            flash('Cigarette entry updated successfully')
        except ValueError:
            flash('Invalid input data')
        
        return redirect(url_for('dashboard'))
    
    return render_template('edit_cigarette.html', cigarette=cigarette)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            current_user.name = request.form['name']
            current_user.age = int(request.form['age'])
            current_user.cigs_per_day = int(request.form['cigs_per_day'])
            current_user.cost_per_cig = float(request.form['cost_per_cig'])
            current_user.currency = request.form['currency']
            current_user.cigs_per_pack = int(request.form['cigs_per_pack'])
            
            db.session.commit()
            flash('Profile updated successfully')
        except ValueError:
            flash('Invalid input data')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    # Delete all cigarettes first due to foreign key constraint
    Cigarette.query.filter_by(user_id=current_user.id).delete()
    
    # Delete the user
    user = User.query.get(current_user.id)
    db.session.delete(user)
    db.session.commit()
    
    # Log out the user
    logout_user()
    flash('Your account has been deleted successfully')
    return redirect(url_for('login'))

@app.route('/update_member_since', methods=['POST'])
@login_required
def update_member_since():
    try:
        new_date = datetime.strptime(request.form['member_since'], '%Y-%m-%d')
        current_user.created_at = new_date
        db.session.commit()
        flash('Member since date updated successfully')
    except ValueError:
        flash('Invalid date format')
    return redirect(url_for('profile'))

@app.context_processor
def inject_stats():
    if current_user.is_authenticated:
        # Get all cigarettes for the user
        cigarettes = Cigarette.query.filter_by(user_id=current_user.id).order_by(Cigarette.smoked_at.desc()).all()
        
        # Calculate max time between cigarettes
        if len(cigarettes) > 1:
            time_diffs = []
            sorted_cigs = sorted(cigarettes, key=lambda x: x.smoked_at)
            for i in range(len(sorted_cigs)-1):
                diff = sorted_cigs[i].smoked_at - sorted_cigs[i+1].smoked_at
                time_diffs.append(abs(diff.total_seconds() / 3600))  # Convert to hours
            max_time_between = max(time_diffs) if time_diffs else 0
        else:
            max_time_between = 0
            
        return {'max_time_between': max_time_between}
    return {}

if __name__ == '__main__':
    # Create the instance directory if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
        
    with app.app_context():
        db.create_all()
    app.run(debug=True) 