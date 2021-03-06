from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import time
import os
from functools import wraps
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_wtf import FlaskForm


app = Flask(__name__)

# app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
#SECRET KEY IS IN .env
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return UserDB.query.get(int(user_id))


##CREATE TABLE IN DB
class UserDB(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


#Line below only required once, when creating DB.
db.create_all()

###### DELETE FROM DB ########
# user = UserDB.query.filter_by(name="rajai").first()
# db.session.delete(user)
# db.session.commit()

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.name != "admin":
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/delete', methods=["GET", "POST"])
@admin_only
def delete():
    all_emails_list = []
    all_emails = UserDB.query.all()
    for mail in all_emails:
        all_emails_list.append(mail)

    if request.method == "POST":
        email = request.form.get('email')
        user = UserDB.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist")
        else:
            db.session.delete(user)
            db.session.commit()
            flash("User Deleted")
            return render_template("delete.html")


    return render_template("delete.html", all_emails_list=all_emails_list)


@app.route('/login', methods=["GET", "POST"])

def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = UserDB.query.filter_by(email=email).first()
        print(user)
        if not user:
            print("Username Does not exist")
            flash("That email does not exist, please try again.")

        elif not check_password_hash(user.password, password):
            print("Wrong Password")
            flash('Password incorrect, please try again..')

        else:
            login_user(user)
            print(current_user.name)
            return render_template("success.html", logged_name=current_user.name)

    return render_template("login.html")




@app.route('/register', methods=["GET", "POST"])
def register():
        if request.method == "POST":
            print(request.form.get('name'))
            print(request.form.get('email'))
            print(request.form.get('password'))
            # name = request.form.get('name')
            email = request.form.get('email')
            # password = request.form.get('password')
            user = UserDB.query.filter_by(email=email).first()
            if user:
                flash("Email already registered, please log in")
                return redirect(url_for('login'))

            else:
                new_user = UserDB(
                    email=request.form.get('email'),
                    name=request.form.get('name'),
                    password=generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
                )


                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return render_template("success.html", logged_name=current_user.name)

        return render_template("register.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/downloads')
@admin_only
def downloads():
    return render_template("downloads.html")

if __name__ == "__main__":
    app.run(debug=True)
