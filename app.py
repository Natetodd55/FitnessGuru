from flask import Flask, request, redirect
from flask.templating import render_template
from flask_login import login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

############################# flask_sql #############################
app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

########################### flask_login ############################
app.config['SECRET_KEY'] = "FitnessGuruProject"
lm = LoginManager(app)
lm.init_app(app)


############################## tables ##############################
class Benefits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(30))
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=True)

class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    cost = db.Column(db.Integer)
    purchase_date = db.Column(db.String(10))
    expiration_date = db.Column(db.String(10))
    member = db.relationship("Member", backref="Membership", lazy='dynamic')
    benefits = db.relationship("Benefits", backref="Membership", lazy='dynamic')


class Member(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email = db.Column(db.String(50))
    phone = db.Column(db.String(10))
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=True)




from app import db, Member, Membership, Benefits
db.create_all()

@lm.user_loader
def load_user(uid):
    return Member.query.get(uid)



############################ flask_routes ###########################
@app.route("/")
def home():
    return render_template("dashboard.html", outline="outline1.html")

@app.route("/login", methods=["POST"])
def login():
    if (request.method=="POST"):
        return render_template("dashboard.html", outline="outline1.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", outline="outline1.html")

@app.route("/membership")
def membership():
    return render_template("membership.html", outline="outline1.html")

@app.route("/training")
def training():
    return render_template("training.html", outline="outline1.html")

