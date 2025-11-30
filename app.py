from datetime import datetime
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import OperationalError
import os
from functools import wraps

app = Flask(__name__)
# Secret key for session and flash messages (replace with a secure value in production)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ToDoList.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Initialize Flask-Migrate (enables `flask db` CLI commands)
migrate = Migrate(app, db)

class ToDo(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    desc = db.Column(db.String(500), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date_created = db.Column(db.DateTime,default = datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User {self.username}>"

@app.route('/', methods = ['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        # require login to create todos
        if not session.get('user_id'):
            flash('Please log in to add todos', 'warning')
            return redirect(url_for('auth'))
        title = request.form['title']
        desc = request.form['desc']
        todo = ToDo(title=title, desc=desc, user_id=session.get('user_id'))
        db.session.add(todo)
        db.session.commit()
    # show only todos for current user
    user_id = session.get('user_id')
    if user_id:
        alltodo = ToDo.query.filter_by(user_id=user_id).all()
    else:
        alltodo = []
    return render_template("index.html", alltodo = alltodo)

@app.cli.command("init-db")
def init_db():
    """Create the database tables."""
    # Flask CLI already runs with an application context, but use app_context() for safety
    with app.app_context():
        db.create_all()
    print("Initialized the database.")


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    """Combined login and signup page. Use form field 'action' to distinguish."""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'signup':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            if not (username and email and password):
                flash('Please fill all signup fields', 'danger')
                return redirect(url_for('auth'))
            try:
                existing = User.query.filter((User.email == email) | (User.username == username)).first()
            except OperationalError:
                # Likely missing tables — create them and retry once
                with app.app_context():
                    db.create_all()
                try:
                    existing = User.query.filter((User.email == email) | (User.username == username)).first()
                except OperationalError:
                    flash('Database not initialized and could not be created automatically. Please run `flask init-db`.', 'danger')
                    return redirect(url_for('auth'))
            if existing:
                flash('User with that email or username already exists', 'warning')
                return redirect(url_for('auth'))
            hashed = generate_password_hash(password)
            user = User(username=username, email=email, password=hashed)
            try:
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash('Could not create account: ' + str(e), 'danger')
                return render_template('auth.html', suggest_signup=True, prefill_email=email, prefill_username=username)
            session['user_id'] = user.id
            flash('Account created and logged in', 'success')
            return redirect(url_for('hello_world'))

        elif action == 'login':
            email = request.form.get('email')
            password = request.form.get('password')
            if not (email and password):
                flash('Please enter email and password', 'danger')
                return redirect(url_for('auth'))
            try:
                user = User.query.filter_by(email=email).first()
            except OperationalError:
                # Table missing — try to create tables and retry once
                with app.app_context():
                    db.create_all()
                try:
                    user = User.query.filter_by(email=email).first()
                except OperationalError:
                    flash('Database not initialized and could not be created automatically. Please run `flask init-db`.', 'danger')
                    return redirect(url_for('auth'))
            if not user:
                # no user with this email — offer to create one
                return render_template('auth.html', suggest_signup=True, prefill_email=email)
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash('Logged in successfully', 'success')
                return redirect(url_for('hello_world'))
            flash('Invalid credentials', 'danger')
            return redirect(url_for('auth'))

    return render_template('auth.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('hello_world'))


@app.context_processor
def inject_user():
    """Inject the currently logged-in user (or None) into template context as `current_user`."""
    user = None
    user_id = session.get('user_id')
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception:
            user = None
    return dict(current_user=user)


@app.route('/profile')
def profile():
    """Show the logged-in user's profile."""
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your profile', 'warning')
        return redirect(url_for('auth'))
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

@app.route('/show')
def show():
    allTodo = ToDo.query.all()
    print(allTodo)
    return "This is the Show Page of ToDo App"


@app.route('/about')
def about():
    """Render the About page describing the project and developer."""
    return render_template('about.html')

@app.route('/update/<int:sno>', methods = ['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        # require login to update
        if not session.get('user_id'):
            flash('Please log in to update todos', 'warning')
            return redirect(url_for('auth'))
        title = request.form['title']
        desc = request.form['desc']
        todo = ToDo.query.filter_by(sno=sno).first()
        # ensure the current user owns this todo
        if not todo or todo.user_id != session.get('user_id'):
            flash('You are not authorized to update this todo', 'danger')
            return redirect(url_for('hello_world'))
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/")
    
    todo = ToDo.query.filter_by(sno=sno).first()
    return render_template("update.html", todo = todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    # require login to delete
    if not session.get('user_id'):
        flash('Please log in to delete todos', 'warning')
        return redirect(url_for('auth'))
    todo = ToDo.query.filter_by(sno=sno).first()
    # ensure the current user owns this todo
    if not todo or todo.user_id != session.get('user_id'):
        flash('You are not authorized to delete this todo', 'danger')
        return redirect(url_for('hello_world'))
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=8000)