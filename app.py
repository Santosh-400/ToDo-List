from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ToDoList.db"
db = SQLAlchemy(app)

class ToDo(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    desc = db.Column(db.String(500), nullable = False)
    date_created = db.Column(db.DateTime,default = datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

@app.route('/', methods = ['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = ToDo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()
    alltodo = ToDo.query.all()
    return render_template("index.html", alltodo = alltodo)

@app.cli.command("init-db")
def init_db():
    """Create the database tables."""
    # Flask CLI already runs with an application context, but use app_context() for safety
    with app.app_context():
        db.create_all()
    print("Initialized the database.")

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
        title = request.form['title']
        desc = request.form['desc']
        todo = ToDo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/")
    
    todo = ToDo.query.filter_by(sno=sno).first()
    return render_template("update.html", todo = todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = ToDo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)