import datetime
import bcrypt
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "#12345@"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=10)


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password_hash = db.Column(db.String(255))
    tasks = db.relationship('Task', backref='user')
    categories = db.relationship('Category', backref='user')

    @property
    def password(self):
        raise AttributeError('')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    db.relationship(
        'tasks', foreign_keys='tasks.category_id')


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    done = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('welcome.html')


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        email = request.form['email']
        new_user = User(first_name=first_name, last_name=last_name,
                        email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    else:
        return render_template('register.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    print(User.query.all())
    if request.method == "POST":
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            password = request.form['password']
            if verify_password(password, user.password_hash):
                session.permanent = True
                email = request.form['email']
                session['id'] = user.id
                session['first_name'] = user.first_name
                session['last_name'] = user.last_name
                session['email'] = user.email
                return redirect(url_for("task_manager"))
            else:
                return "<h2>Wrong email or password</h2>"
        else:
            return "<h2>No user</h2>"
    else:
        if "user" in session:
            return redirect(url_for("user"))
        else:
            return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop("id", None)
    session.pop("first_name", None)
    session.pop("last_name", None)
    session.pop("email", None)
    return redirect(url_for("login"))


@app.route('/task_manager', methods=['POST', 'GET'])
@login_required
def task_manager():
    print(session)
    if request.method == "POST":
        if 'title' in request.form:
            title = request.form['title']
            description = request.form['description']
            category = request.form['category']
            user_id = request.form['user_id']
            new_task = Task(title=title, category_id=category,
                            description=description, user_id=user_id)
            db.session.add(new_task)
            db.session.commit()
        else:
            name = request.form['category_name']
            user_id = request.form['user_id']
            new_category = Category(name=name, user_id=user_id)
            db.session.add(new_category)
            db.session.commit()
    tasks = Task.query.filter_by(user_id=session['id']).all()
    categories = Category.query.filter_by(user_id=session['id']).all()
    return render_template('task_manager.html', tasks=tasks, categories=categories, session=session)


@app.route('/edit_task/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_task(id):
    if request.method == "POST":
        task = Task.query.filter_by(id=id).first()
        task.title = request.form['title']
        task.category = request.form['category']
        task.description = request.form['description']
        db.session.commit()
        return redirect(url_for('task_manager'))

    task = Task.query.filter_by(id=id).first()
    categories = Category.query.filter_by(user_id=session['id']).all()
    return render_template('edit_task.html', task=task, categories=categories, session=session)


@app.route('/delete_task/<int:id>')
@login_required
def delete_task(id):
    task = Task.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("task_manager"))


@app.route('/finish_task/<int:id>')
@login_required
def finish_task(id):
    task = Task.query.filter_by(id=id).first()
    task.done = True
    db.session.commit()
    return redirect(url_for("task_manager"))


db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
