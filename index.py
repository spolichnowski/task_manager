from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import datetime


app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "#12345@"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=10)


db = SQLAlchemy(app)


# class User(db.Model):
#     __tablename__ = 'users'
#     _id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120))

#     def __init__(self, email):
#         self.email = email


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
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


@app.route('/')
def index():
    return render_template('welcome.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form['email']
        session['user'] = user
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        else:
            return render_template('login.html')


@app.route('/user', methods=['POST', 'GET'])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        if request.method == 'POST':
            email = request.form['email']
            session['email'] = email
        else:
            if 'email' in session:
                email = session['email']
        return f"<h1>{user}</h1>"
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return redirect(url_for("login"))


@app.route('/logout')
def logout():
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))


@app.route('/task_manager', methods=['POST', 'GET'])
def task_manager():
    if request.method == "POST":
        if 'title' in request.form:
            title = request.form['title']
            description = request.form['description']
            category = request.form['category']
            # category_id = Category.query.filter_by(name=category).first
            new_task = Task(title=title, category_id=category,
                            description=description)
            db.session.add(new_task)
            db.session.commit()
        else:
            name = request.form['category_name']
            new_category = Category(name=name)
            db.session.add(new_category)
            db.session.commit()

    tasks = Task.query.all()
    categories = Category.query.all()
    print(categories[0].name)
    return render_template('task_manager.html', tasks=tasks, categories=categories)


@app.route('/delete_task/<int:id>')
def delete_task(id):
    task = Task.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("task_manager"))


@app.route('/finish_task/<int:id>')
def finish_task(id):
    task = Task.query.filter_by(id=id).first()
    task.done = True
    db.session.commit()
    return redirect(url_for("task_manager"))


# db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
