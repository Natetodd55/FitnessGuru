from flask import Flask, request, redirect
from flask.templating import render_template
from flask_login import login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_simple_crypt import SimpleCrypt

############################# flask_sql #############################
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

########################### flask_login ############################
app.config['SECRET_KEY'] = "FitnessGuruProject"
lm = LoginManager(app)
lm.init_app(app)

########################### flask_encryption #############################
cipher = SimpleCrypt()
cipher.init_app(app)

############################### tables ##############################
class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(5))
    date = db.Column(db.String(10))
    instructor = db.Column(db.String(50))
    benefit_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=True)

class Benefits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(30), db.ForeignKey('services.service_name'), nullable=False)
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=True)
    services = db.relationship('Services', backref='Benefits')


class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    purchase_date = db.Column(db.String(10), nullable=False)
    expiration_date = db.Column(db.String(10), nullable=False)
    member = db.relationship("Member", backref="Membership", lazy='dynamic')
    benefits = db.relationship("Benefits", backref="Membership", lazy='dynamic')

class Member(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(75), nullable=False)
    phone = db.Column(db.String(10))
    authenticated = db.Column(db.Boolean, default=False)
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=True)
    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_anonymous(self):
        return False


@lm.user_loader
def load_user(uid):
    return Member.query.get(uid)

# from app import db, User
# db.create_all()

############################ flask_routes ###########################
@app.route("/")
def home():
    return render_template("dashboard.html", outline="outline1.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method=="POST"):
        email = request.form['email']
        member = Member.query.filter_by(email=email).first()
        if member:
            if request.form['password'] == cipher.decrypt(member.password).decode('utf-8'):
                member.authenticated = True
                db.session.add(member)
                db.session.commit()
                login_user(member, remember=True)
                return render_template('dashboard.html')

    return render_template('login.html')

@app.route("/create_member", methods=["GET", "POST"])
def create_member():
    message = None
    if (request.method=="POST"):
        f_name = request.form['first_name']
        l_name = request.form['last_name']
        email = request.form['email']
        if Member.query.filter_by(email=email).first() == None:
            member_pass = cipher.encrypt(request.form['password'])
            member = Member(first_name = f_name, last_name=l_name, email=email, password=member_pass)
            db.session.add(member)
            db.session.commit()
            login_user(member, remember=True)
            return render_template('dashboard.html')
        else:
            message = "Member already registered with email: "+email

    return render_template('create_member.html', message=message)

@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template('dashboard.html')


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", outline="outline1.html")

@app.route("/membership")
def membership():
    return render_template("membership.html", outline="outline1.html")

@app.route("/training")
def training():
    services = db.session.query(Services) \
        .join(Benefits, Services.benefit_id == Benefits.id) \
        .join(Membership, Benefits.membership_id == Membership.id) \
        .join(Member, Membership.id == Member.membership_id) \
        .filter(Member.id == current_user.id) \
        .all()

    for service in services:
        print(f"Service Name: {service.service_name}")
        print(f"Time: {service.time}")
        print(f"Date: {service.date}")
        print(f"Instructor: {service.instructor}")
        print("----------------\n")

    return render_template("training.html")

if __name__ == "__main__":
    app.run(debug=True)

