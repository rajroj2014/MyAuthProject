from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import time
import os

app = Flask(__name__)

# app.config['SECRET_KEY'] = 'ý{Hå<ùã.5ÑO<!Õ¢ R"¡¨'
app.config['SECRET_KEY'] = os.environ.get("any-secret-key-you-choose")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://yruhjwfaczymsm:b925fac7bf4c698b5074180cb502fd982997f197b040e396bea6058c0f0498f6@ec2-3-233-7-12.compute-1.amazonaws.com:5432/d38atpjju3ivpd'
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


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/delete', methods=["GET", "POST"])
def delete():
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


    return render_template("delete.html")


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
            flash("That email exist, Redirecting to log in page")
            return redirect(url_for('login'))

        else:
            new_user = UserDB(
                email=request.form.get('email'),
                name=request.form.get('name'),
                password=generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
            )


            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home'))



    return render_template("register.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
