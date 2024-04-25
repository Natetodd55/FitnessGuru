from flask import Flask, request, redirect
from flask.templating import render_template
# from flask_login import login_manager
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

############################# flask_sql #############################
app = Flask(__name__)
# db = SQLAlchemy(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

############################ flask_login ############################
# app.config['SECRET_KEY'] = "FitnessGuruProject"
# lm = LoginManager(app)
# lm.init_app(app)

# @lm.user_loader
# def load_user(uid):
#     return User.query.get(uid)

############################### tables ##############################
# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20))
#     age = db.Column(db.Integer)
#     username = db.Column(db.String(20), unique=True)
#     password = db.Column(db.String(40))

# from app import db, User
# db.create_all()

############################ flask_routes ###########################
@app.route("/dashboard")
def home():
    return render_template("dashboard.html", outline="outline1.html")

@app.route("/membership")
def home():
    return render_template("membership.html", outline="outline1.html")

@app.route("/training")
def home():
    return render_template("training.html", outline="outline1.html")
